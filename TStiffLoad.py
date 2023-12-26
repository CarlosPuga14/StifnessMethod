#%% --------------------------
#       IMPORTED MODULES
# ----------------------------
import sys
import numpy as np
from dataclasses import dataclass, field

@dataclass
class TStiffLoad:
#%% --------------------------
#       DOC STRING
# ----------------------------
    """
    Provides the forces created by an applied load_type.

    Currently are available for 'load_type':
        - 'uniform load_type'
        - 'nodal force'

    More information is required in a dictionary:
        - In case of "uniform load": {"load": _, "length": _}
            * load = magnitude of applied load
            * length = element length on which the load is applied
        - In case of "nodal force": {"force": _, "a": _, "b": _}
            * force = applied nodal force magnitude
            * a = distance from the left node
            * b = distance from the right node
    """
#%% --------------------------
#       INITIALIZER
# ----------------------------
    _load_type: tuple[str, dict[str, float]] = field(default_factory=tuple)
    _reaction_forces: np.ndarray = field(init=False, default=np.zeros(6))

    def __post_init__(self):
        self._reaction_forces = self.calc_reaction_forces()

#%% --------------------------
#       GETTERS & SETTERS
# ----------------------------
    @property
    def load_type(self): return self._load_type
    @load_type.setter
    def load_type(self, load): self._load = load

    @property
    def reaction_forces(self): return self._reaction_forces
    @reaction_forces.setter
    def reaction_forces(self, reaction_forces): self._reaction_forces = reaction_forces

#%% --------------------------
#       CLASS MODULES
# ----------------------------
    def calc_reaction_forces(self)->np.ndarray:
        """
        Evalutes the reaction forces of a given load type
        """
        load_type, kwargs = self.load_type

        if load_type == "uniform load": 
            q = kwargs["load"]
            l = kwargs["length"]

            return np.array([0, q*l/2, q*l**2/12, 0, q*l/2, -q*l**2/12])

        elif load_type == "nodal force": 
            P = kwargs["force"]
            a = kwargs["a"]
            b = kwargs["b"]
            l = a + b
            return np.array([0, P*b**2*(3*a+b)/l**3, P*a*b**2/l**2, 0, P*a**2*(a+3*b)/l**3, -P*a**2*b/l**2])
        else:
            print(f"ERROR: load type not defined ({load_type})")
            sys.exit()
