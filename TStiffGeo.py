#%% --------------------------
#       IMPORTED MODULES
# ----------------------------
from dataclasses import dataclass, field
import math

@dataclass
class TStiffGeo:
#%% --------------------------
#       DOC STRING
# ----------------------------
    """
    Provides the geometric properties of a given cross section type.
    
    Currently it is available for 'section_type':
        - "Rectangle"
        - "Circular"

    Complementar information must be provided in a dictionary
        - In case of Rectangle, provide the base and height size {"base": value, "height": value}
        - In case of Circular, provide the radius size {"radius": value}
    """
#%% --------------------------
#       INITIALISER
# ----------------------------
    _section_type: tuple[str, dict[str, float]]
    _area: float = field(init=False)
    _inertia: float = field(init=False)

    def __post_init__(self):
        self._area = self.CalcArea()
        self._inertia = self.CalcInertia()

#%% --------------------------
#       GETTERS & SETTERS
# ----------------------------
    @property
    def section_type(self): return self._section_type
    @section_type.setter
    def section_type(self, sectype): self._section_type = sectype

    @property
    def area(self): return self._area
    @area.setter
    def area(self, area): self._area = area

    @property
    def inertia(self): return self._inertia
    @inertia.setter
    def inertia(self, inertia): self._inertia = inertia

#%% --------------------------
#       CLASS METHODS
# ----------------------------
    def CalcArea(self)->float:
        """
        Calculates the area of a given cross section
        """
        geo_type, properties = self._section_type

        if geo_type == "Rectangle":
            base = properties["base"]
            height = properties["height"]
            return base*height
        
        elif geo_type == "Circular":
            radius = properties["radius"]
            return math.pi*radius**2
        
    def CalcInertia(self)->float:
        """
        Calculates the inertia moment of a given cross section
        """
        geo_type, properties = self._section_type

        if geo_type == "Rectangle":
            base = properties["base"]
            height = properties["height"]
            return base*height**3/12
        
        elif geo_type == "Circular":
            radius = properties["radius"]
            return math.pi*radius**4/4