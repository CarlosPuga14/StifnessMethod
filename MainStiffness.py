"""
Script to solve structures using the 
Stiffness Method

Created by Carlos Puga: 12/19/23
"""
#%% --------------------------
#         Imported Modules
# ----------------------------
from TStiffNode import TStiffNode
from TStiffGeo import TStiffGeo
from TStiffMech import TStiffMech
from TStiffElement import TStiffElement
from TStiffLoad import TStiffLoad
from TStiffAnalysis import TStiffAnalysis

#%% --------------------------
#         MAIN FUNCTION
# ----------------------------
def main():
    section_rec = TStiffGeo(_section_type = ("Rectangle", {"base": 10, "height": 10}))

    material = TStiffMech(_E = 25e6, _poisson = 0.3)

    n1 = TStiffNode(_coordinates= [0,0], _support_type = "Fixed")
    n2 = TStiffNode(_coordinates = [0,1], _support_type = 'Free')
    n2.is_hinge()

    element = TStiffElement(_nodes = [n1,n2], _mechanical_prop = material, _geometric_prop = section_rec)

    uniform_load = TStiffLoad(_load_type = ("uniform load", {"load": 10, "length": element.length}))
    nodal_force = TStiffLoad(_load_type = ("nodal force", {"force": 5, "a": 0, "b":element.length}))

    element.Apply_loads([uniform_load, nodal_force])

    an = TStiffAnalysis([element])
    an.find_DoF()

    print(element)
    print(an)

if __name__ == "__main__":
    main()