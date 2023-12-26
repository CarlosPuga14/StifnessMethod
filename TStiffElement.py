#%% --------------------------
#       IMPORTED MODULES
# ----------------------------
import sys
import numpy as np
from dataclasses import dataclass, field
from TStiffNode import TStiffNode
from TStiffMech import TStiffMech
from TStiffGeo import TStiffGeo
from TStiffLoad import TStiffLoad

@dataclass
class TStiffElement:
#%% --------------------------
#       DOC STRING
# ----------------------------
    """
    Stores all the required information to perform the Stiffness Method
    in an element.

    Provide:
        - nodes: list of element nodes
        - mechanical_prop: element mechanical properties
        - geometric_prop: element geometric properties
        
    Computed:
        - length: element length
        - angle: element inclination angle
        - fel: element load vector
        - kel: element stiffness matrix
    """
#%% --------------------------
#         INITIALISER
# ----------------------------
    _nodes: list[TStiffNode]
    _mechanical_prop: TStiffMech
    _geometric_prop: TStiffGeo
    _length: float = field(init=False)
    _angle: float = field(init=False)
    _fel: np.ndarray = field(init=False, default= np.zeros(6))
    _kel: np.ndarray = field(init=False, default=np.zeros((6,6)))

    def __post_init__(self):
        self._length = self.Distance()
        self._angle = self.Angle()

#%% --------------------------
#         GETTER & SETTER
# ----------------------------
    @property
    def nodes(self): return self._nodes
    @nodes.setter
    def nodes(self, nodes): self._nodes = nodes

    @property
    def mechanical_prop(self): return self._mechanical_prop
    @mechanical_prop.setter
    def mechanical_prop(self, properties): self._mechanical_prop = properties

    @property
    def geometric_prop(self): return self._geometric_prop
    @geometric_prop.setter
    def geometric_prop(self, properties): self._geometric_prop = properties
        
    @property
    def length(self): return self._length
    @length.setter
    def length(self, length): self._length = length
        
    @property
    def angle(self): return self._angle
    @angle.setter
    def angle(self, angle): self._angle = angle

    @property
    def fel(self): return self._fel
    @fel.setter
    def fel(self, load_vector): self._fel = load_vector

    @property
    def kel(self): return self._kel
    @kel.setter
    def kel(self, stiffness_matrix): self._kel = stiffness_matrix

#%% --------------------------
#        CLASS METHODS
# ----------------------------
    def Distance(self)->float:
        """
        Calculates the euclidean norm between two points
        """
        node1, node2 = self.nodes
        return np.linalg.norm(node2.coordinates-node1.coordinates)
    
    def Angle(self)->float:
        """
        Calculates the inclination angle between two points
        """
        node1, node2 = self.nodes
        dy = (node2.coordinates - node1.coordinates)[1]

        return np.arcsin(dy/self.length)
    
    def check_values(self, load:TStiffLoad)->bool:
        """
        Check whether the load values are consistent or not
        """        
        type, kwargs = load.load_type
        
        if type == "uniform load":
            if kwargs["length"] > self.length:
                print(f"Applied load length greater than element length ({kwargs['length']} > {self.length})")
                return False
        elif type == "nodal force":
            if kwargs["a"] + kwargs["b"] > self.length:
                print(f"a + b greater than element length ({kwargs['a']} + {kwargs['b']} > {self.length})")
                return False
        return True 

    def Apply_loads(self, load_vector:list[TStiffLoad])->None:
        """ 
        Modify the element load vector, applying loads
        """
        for load in load_vector:
            if not self.check_values(load):
                print("ERROR: Load term inconsistent")
                sys.exit()

            self.fel += load.reaction_forces
