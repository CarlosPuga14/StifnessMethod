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
def main()->int:
    section_rec = TStiffGeo(_section_type = ("Rectangle", {"base": 0.222223, "height": 0.6}))
    material = TStiffMech(_E = 25e6, _poisson = 0.3) 

    n1 = TStiffNode(_coordinates= [0,0], _support_type = 'Pinned')
    n2 = TStiffNode(_coordinates = [1,0], _support_type = 'Pinned')

    element = TStiffElement(_nodes = [n1,n2], _mechanical_prop = material, _geometric_prop = section_rec)

    uniform_load = TStiffLoad(_load_type = ("uniform load", {"load": 10, "length": element.length}))

    element.Apply_loads([uniform_load])

    structure = [element]

    an = TStiffAnalysis(structure)
    an.Run()
    an.print_results()

    return 0

if __name__ == "__main__":
    main()