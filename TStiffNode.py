#%% --------------------------
#       IMPORTED MODULES
# ----------------------------
from dataclasses import dataclass, field
import numpy as np

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
    """
#%% --------------------------
#       INITIALIZER
# ----------------------------
    _coordinates: list
    _support_type: str = "Free"
    _hinge: bool = field(init=False, default=False)
    _DoF: list[int] = field(init=False, default_factory=list)

    def __post_init__(self):
        self._coordinates = np.array(self._coordinates)
        self._DoF = [np.nan for _ in range(3)]
 

#%% --------------------------
#       GETETRS & SETTERS
# ----------------------------
    @property
    def coordinates(self): return self._coordinates
    @coordinates.setter
    def coordinates(self, coordinates): self.coordinates = coordinates
        
    @property
    def support_type(self): return self._support_type
    @support_type.setter
    def support_type(self, support): self.support_type = support

    @property
    def hinge(self): return self._hinge
    @hinge.setter
    def hinge(self, is_hinge): self._hinge = is_hinge

    @property
    def DoF(self): return self._DoF
    @DoF.setter
    def DoF(self, DoF): self.DoF = DoF

#%% --------------------------
#       CLASS METHODS
# ----------------------------
    def is_hinge(self):
        self.hinge = True
        self.DoF.append(np.nan)