#%% --------------------------
#       IMPORTED MODULES
# ----------------------------
import numpy as np
from dataclasses import dataclass, field
from typing import ClassVar
from tpanic import DebugStop
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
        - 'nodes': list of element nodes
        - 'mechanical_prop': element mechanical properties
        - 'geometric_prop': element geometric properties
        
    Computed:
        - 'length': element length
        - 'angle': element inclination angle
        - 'fel': element load vector
        - 'uel': element displacement vector
        - 'kel': element stiffness matrix
        - 'rotation_matrix': element roational matrix
    """
#%% --------------------------
#         INITIALIZER
# ----------------------------
    counter: ClassVar[int] = 0

    _nodes: list[TStiffNode]
    _mechanical_prop: TStiffMech
    _geometric_prop: TStiffGeo
    _index: int = field(init=False)
    _length: float = field(init=False)
    _angle: float = field(init=False)
    _fel: np.ndarray = field(init=False)
    _uel: np.ndarray = field(init=False)
    _kel: np.ndarray = field(init=False)
    _rotation_matrix: np.ndarray = field(init=False)

    def __post_init__(self):
        self.length = self.Distance()
        self.angle = self.Angle()
        self.element_index()
        self.fel = np.zeros(6)
        self.uel = np.zeros_like(self.fel)
        self.rotation_matrix = np.zeros((6,6))
        self.kel = np.zeros_like(self.rotation_matrix)

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
    def length(self, l): self._length = l
        
    @property
    def angle(self): return self._angle
    @angle.setter
    def angle(self, theta): self._angle = theta

    @property
    def fel(self): return self._fel
    @fel.setter
    def fel(self, load_vector): self._fel = load_vector

    @property
    def uel(self): return self._uel
    @uel.setter
    def uel(self, displacement): self._uel = displacement

    @property
    def kel(self): return self._kel
    @kel.setter
    def kel(self, stiff_mat): self._kel = stiff_mat
    
    @property
    def rotation_matrix(self): return self._rotation_matrix
    @rotation_matrix.setter
    def rotation_matrix(self, rotation): self._rotation_matrix = rotation

    @property
    def index(self): return self._index
    @index.setter
    def index(self, i): self._index = i

#%% --------------------------
#        CLASS METHODS
# ----------------------------
    @classmethod
    def increment_counter(cls):
        cls.counter += 1
        
    def element_index(self):
        self.index = self.counter
        TStiffElement.increment_counter()

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
                DebugStop()
                
            self.fel += load.reaction_forces

    def get_element_equations(self)->list[int]:
        index = 0
        dof_list = []
        for node in self.nodes:
            if node.hinge and index == 1:
                dof_list += node.DoF[:3]
            elif node.hinge and index == 0:
                dof_list += node.DoF[:2] + [node.DoF[3]]
            else:
                dof_list += node.DoF
            index+=1

        return dof_list

    def rotate(self):
        """
        Evaluates the element rotational matrix 
        """

        lx = np.cos(self.angle)
        ly = np.sin(self.angle)

        self.rotation_matrix = np.array([
            [lx, ly, 0, 0, 0, 0], 
            [-ly, lx, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, lx, ly, 0], 
            [0, 0, 0, -ly, lx, 0],
            [0, 0, 0, 0, 0, 1]
        ])

    def calc_stiff(self):
        """
        Evaluates the element stiffness matrix
        """
        EA = self.mechanical_prop.E*self.geometric_prop.area
        EI = self.mechanical_prop.E*self.geometric_prop.inertia
        l = self.length

        truss_stiffness = np.array([
            [EA/l, 0, 0, -EA/l, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [-EA/l, 0, 0, EA/l, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0]
        ])  

        beam_stiffness = np.array([
            [0, 0, 0, 0, 0, 0],
            [0, 12*EI/l**3, 6*EI/l**2, 0, -12*EI/l**3, 6*EI/l**2],
            [0, 6*EI/l**2, 4*EI/l, 0, -6*EI/l**2, 2*EI/l],
            [0, 0, 0, 0, 0, 0],
            [0, -12*EI/l**3, -6*EI/l**2, 0, 12*EI/l**3, -6*EI/l**2],
            [0, 6*EI/l**2, 2*EI/l, 0, -6*EI/l**2, 4*EI/l]
        ])

        kloc = truss_stiffness + beam_stiffness

        self.kel = np.transpose(self.rotation_matrix)@kloc@self.rotation_matrix