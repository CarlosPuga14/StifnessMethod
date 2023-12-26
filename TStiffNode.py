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
        - DoF: node Degrees of Freedom
    """
#%% --------------------------
#       INITIALISER
# ----------------------------
    _coordinates: list
    _DoF: list[int]

    def __post_init__(self):
        self._coordinates = np.array(self._coordinates)

#%% --------------------------
#       GETETRS & SETTERS
# ----------------------------
    @property
    def coordinates(self): return self._coordinates
    @coordinates.setter
    def coordinates(self, coordinates): self._coordinates = coordinates
        
    @property
    def DoF(self): return self._DoF
    @DoF.setter
    def DoF(self, DoF): self._DoF = DoF
        