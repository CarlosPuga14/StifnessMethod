#%% --------------------------
#       IMPORTED MODULES
# ----------------------------
import numpy as np
from typing import ClassVar
from tpanic import DebugStop
from dataclasses import dataclass, field

@dataclass
class TStiffNode:
#%% --------------------------
#       DOC STRING
# ----------------------------
    """
    Stores the required data in each node to perform the Stiffness Method
        - coordinates: node coordinates
        - support_type: node support type. Currently available:
            * 'Free': frees all degrees of freedom
            * 'RollerX': frees the x displacement and rotation
            * 'RollerY': frees the y displacement and rotation
            * 'Pinned': frees the rotation
            * 'Fixed': constrains all degrees of freedom
        - hinge: set the node as a hinge
        - DoF: node Degrees of Freedom
        - springs: list contaning informations about nodal prescribed springs. 
        - displacement: list containing information about nodal prescribed displacement. 
    """
#%% --------------------------
#       INITIALIZER
# ----------------------------
    counter: ClassVar[int] = 0

    _coordinates: list
    _support_type: str = "Free"
    _index: int = field(init=False)
    _hinge: bool = field(init=False, default=False)
    _number_of_connections: int = field(init=False, default=0)
    _connects: list = field(init=False, default_factory=list)
    _DoF: list[int] = field(init=False, default_factory=list)
    _springs: list[tuple[str, float]] = field(init=False, default_factory=list)
    _nodal_displacement: list[tuple[str, float]] = field(init=False, default_factory=list)

    def __post_init__(self):
        self._coordinates = np.array(self._coordinates)
        self.node_index()
        self._DoF = [np.nan for _ in range(3)]
 
#%% --------------------------
#       GETETRS & SETTERS
# ----------------------------
    @property
    def coordinates(self): return self._coordinates
    @coordinates.setter
    def coordinates(self, coordinates): self._coordinates = coordinates
        
    @property
    def support_type(self): return self._support_type
    @support_type.setter
    def support_type(self, support): self._support_type = support

    @property
    def hinge(self): return self._hinge
    @hinge.setter
    def hinge(self, is_hinge): self._hinge = is_hinge

    @property
    def DoF(self): return self._DoF
    @DoF.setter
    def DoF(self, DoF): self._DoF = DoF

    @property
    def springs(self): return self._springs
    @springs.setter
    def springs(self, spring): self._springs = spring

    @property
    def nodal_displacement(self): return self._nodal_displacement
    @nodal_displacement.setter
    def nodal_displacement(self, disp): self._nodal_displacement = disp

    @property
    def index(self): return self._index
    @index.setter
    def index(self, i): self._index = i

    @property
    def connects(self): return self._connects
    @connects.setter
    def connects(self, c): self._connects = c

    @property
    def number_of_connections(self): return self._number_of_connections
    @number_of_connections.setter
    def number_of_connections(self, n): self._number_of_connections = n

#%% --------------------------
#       CLASS METHODS
# ----------------------------
    @classmethod
    def increment_counter(cls):
        cls.counter += 1
        
    def node_index(self):
        self.index = self.counter
        TStiffNode.increment_counter()

    def is_hinge(self):
        self.hinge = True

    def prescribed_displacement(self, displacements:list[tuple[str, float]]):
        """
        Stores and prescribes a displacement to a node.

        Currently available:
            - 'Xdisp': prescribed displacement in the x direction
            - 'Ydisp': prescribed displacement in the y direction
            - 'Rot': prescribed rotation
        """
        check_support = {'Free': [], 'RollerX': ['Ydisp'], 'RollerY': ['Xdisp'], 
                         'Pinned': ['Xdisp','Ydisp'], 'Fixed': ['Xdisp','Ydisp','Rot']}
        
        for item in displacements:
            disp_type, value = item

            if  disp_type in check_support[self.support_type]:
                self.nodal_displacement.append((disp_type, value))
            else:
                print(f"ERROR: You cannot prescribed a {disp_type} displacement to a {self.support_type} support")
                DebugStop()

    def prescribed_spring(self, springs: list[tuple[str, float]]):
        """
        Sotres and prescribes springs to the node.

        Currently available:
            - 'TransX': tranlational spring in the x direction
            - 'TransY': tranlational spring in the y direction
            - 'Rot': rotational spring 
        """
        check_spring = {'Free': ['TransX', 'TransY', 'Rot'], 'RollerX': ['TransX', 'Rot'], 
                        'RollerY':['TransY', 'Rot'], 'Pinned': ['Rot'], 'Fixed': []}

        for item in springs:
            spring_type, value = item

            if spring_type in check_spring[self.support_type]:
                self.springs.append((spring_type, value))
            else:
                print(f"ERROR: You cannot prescribed a {spring_type} spring to a {self.support_type} support")
                DebugStop()