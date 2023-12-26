#%% --------------------------
#       IMPORTED MODULES
# ----------------------------
from dataclasses import dataclass, field

@dataclass
class TStiffMech:
#%% --------------------------
#       DOC STRING
# ----------------------------
    """
    Provides the mechanical properties of a given material.
        - E: Young Modulus
        - poisson: Poisson Ration
        - G: Shear Modulus (authomaticallu computed)
    """
#%% --------------------------
#       INITIALIZER
# ----------------------------
    _E: float
    _poisson: float 
    _G: float = field(init=False)

    def __post_init__(self): 
        self._G = self.E/(1+self.poisson)

#%% --------------------------
#       GETTERS & SETTERS
# ----------------------------
    @property
    def E(self): return self._E
    @E.setter
    def E(self, E): self.E = E

    @property
    def poisson(self): return self._poisson
    @poisson.setter
    def poisson(self, poisson): self.poisson = poisson

    @property
    def G(self): return self._G
    @G.setter
    def G(self, G): self.G = G