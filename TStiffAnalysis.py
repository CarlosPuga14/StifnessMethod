#%% --------------------------
#       IMPORTED MODULES
# ----------------------------
from dataclasses import dataclass, field 
from TStiffElement import TStiffElement
from TStiffNode import TStiffNode
import numpy as np 

@dataclass
class TStiffAnalysis:
#%% --------------------------
#       DOC STRING
# ----------------------------
    """
    Class developed to perform the Stiffness Method for structural analysis

    Fields:
        - 'elements': list containing each element of the structure
        - 'nodes_list': list containing each node of the structure
        - 'number_equations': total numbe of equation of the system
        - 'number_free_equations': number of equations used to find the displacements
    """
#%% --------------------------
#       INITIALIZER
# ----------------------------
    _elements: list[TStiffElement]
    _nodes_list: list[TStiffNode] = field(init=False, repr=False, default_factory=list)
    _number_equations: int = field(init=False, default=0)
    _number_free_equations: int = field(init=False)
    _FG: np.ndarray = field(init=False)
    _UG: np.ndarray = field(init=False)
    _KG: np.ndarray = field(init=False)

    def __post_init__(self):
        self.find_nodes()
        self.find_equations()
        self.FG = np.zeros(self.number_equations)
        self.UG = np.zeros_like(self.FG)
        self.KG = np.zeros((self.number_equations, self.number_equations))
        

#%% --------------------------
#       SETTERS & GETTERS
# ----------------------------
    @property
    def elements(self): return self._elements
    @elements.setter
    def elements(self, elements: list[TStiffElement]): self._elements = elements

    @property
    def nodes_list(self): return self._nodes_list
    @nodes_list.setter
    def nodes_list(self, nodes: list[TStiffNode]): self._nodes_list = nodes

    @property
    def number_equations(self): return self._number_equations
    @number_equations.setter
    def number_equations(self, n_equations): self._number_equations = n_equations

    @property
    def number_free_equations(self): return self._number_free_equations
    @number_free_equations.setter
    def number_free_equations(self, free_equations): self._number_free_equations = free_equations

    @property
    def FG(self): return self._FG
    @FG.setter
    def FG(self, fg): self._FG = fg

    @property
    def UG(self): return self._UG
    @UG.setter
    def UG(self, ug): self._UG = ug

    @property
    def KG(self): return self._KG
    @KG.setter
    def KG(self, kg): self._KG = kg
#%% --------------------------
#       CLASS METHODS
# ----------------------------
    def find_nodes(self)->None:
        """
        Concatenates every node in the structure, making sure it 
        only appears once
        """
        for element in self.elements:
            for node in element.nodes:
                if not any(n.index == node.index for n in self.nodes_list):
                    self.nodes_list.append(node)

    def find_equations(self)->None:
        """
        Find the total number of equations in the system and 
        the number of free equations used to solve the displacements
        """
        self.calc_free_equations()
        self.number_free_equations = self.number_equations

        self.calc_constrained_equations()

    def set_node_DoF(self, node:TStiffNode, dof:list[int]):
        """
        Sets the degrees of freedom ('dof') in a given 'node'. 
        """
        for i in dof:
            node.DoF[i] = self.number_equations
            self.number_equations += 1

    def calc_free_equations(self):
            """
            Calculates the number of free equations in the system
            """
            support_free_equations = {'Free': [0,1,2], 'RollerX': [0,2], 'RollerY': [1,2], 'Pinned': [2]}

            for node in self.nodes_list:
                if node.support_type == 'Free':
                    self.set_node_DoF(node, support_free_equations['Free'])
                
                elif node.support_type == 'RollerX':
                    self.set_node_DoF(node, support_free_equations['RollerX'])

                elif node.support_type == 'RollerY':
                    self.set_node_DoF(node, support_free_equations['RollerY'])

                elif node.support_type == 'Pinned':
                    self.set_node_DoF(node, support_free_equations['Pinned'])

                if node.hinge:
                    for _ in range(node.number_of_connections-1):
                        node.DoF.append(self.number_equations)
                        self.number_equations += 1

    def calc_constrained_equations(self):
            """
            Calculates the number of constrained equations in the system
            """
            support_constrained_equations = {'RollerX': [1], 'RollerY': [0], 'Pinned': [0,1], 'Fixed': [0,1,2]}

            for node in self.nodes_list:
                if node.support_type == 'RollerX':
                    self.set_node_DoF(node, support_constrained_equations['RollerX'])

                elif node.support_type == 'RollerY':
                    self.set_node_DoF(node, support_constrained_equations['RollerY'])

                elif node.support_type == 'Pinned':
                    self.set_node_DoF(node, support_constrained_equations['Pinned'])
                
                elif node.support_type == "Fixed":
                    self.set_node_DoF(node, support_constrained_equations['Fixed'])
  
    def check_for_prescribed_displacements(self):
        disp_to_DoF = {'Xdisp': 0, 'Ydisp': 1, 'Rot': 2}
        
        for node in self.nodes_list:
            for disp in node.nodal_displacement:
                disp_type, value = disp

                dof = node.DoF[disp_to_DoF[disp_type]]
                self.UG[dof] += value

    def check_for_prescribed_springs(self):
        spring_to_DoF = {'TransX': 0, 'TransY': 1, 'Rot': 2}

        for node in self.nodes_list:
            for spring in node.springs:
                spring_type, value = spring

                dof = node.DoF[spring_to_DoF[spring_type]]
                self.KG[dof, dof] += value
   
    def assemble(self, element:TStiffElement):
        element.get_element_equations()

        for i, dof_i in enumerate(element.equations):
            self.FG[dof_i] += element.fel[i]

            for j, dof_j in enumerate(element.equations):
                self.KG[dof_i, dof_j] += element.kel[i, j]

    def find_element_solution(self):
        for e in self.elements:
            for i, equation in enumerate(e.equations):
                e.uel[i] += self.UG[equation]
            
            e.solution = np.dot(e.kel, e.uel) - e.fel

    def Run(self)->None:
        self.check_for_prescribed_displacements()

        for element in self.elements:
            element.rotate()
            element.calc_stiff()

            self.assemble(element)

        self.check_for_prescribed_springs()

        K00 = self.KG[:self.number_free_equations, :self.number_free_equations]
        F0 = self.FG[:self.number_free_equations]
        
        u0 = np.dot(np.linalg.inv(K00), F0)
        self.UG[:self.number_free_equations] += u0

        self.find_element_solution()

    def Results(self, variables: list[str], file: str = None)->None:
        """
        Prints simulation results and 
        element data

        Options available:
            - 'info': element data
            - 'fel': element load vector
            - 'uel': element displacements
            - 'kel': element stiffness matrix
            - 'rot': element rotation matrix
            - 'sol': element reaction forces
        """
        def print_vector(vector, notation=1):
            end = ', '
            for i, value in enumerate(vector):
                if i == len(vector)-1:
                    end = '\n'
                if notation:
                    nprint(f"{value:.2e}", e=end)
                else:
                    nprint(f"{value}", e=end)
        
        def print_matrix(matrix, notation=1):
            for row in (matrix):
                end = ', '
                for j, col in enumerate(row):
                    if j == len(row)-1:
                        end = '\n'
                    if notation: 
                        nprint(f"{col:.2e}", e=end)
                    else:
                        nprint(f"{col}", e=end)
        
        def print_reults(file):
            nprint(f"{'='*15} ELEMENT RESULTS {'='*15}")

            for e in self.elements:
                nprint(f"* Index: {e.index}")
                nprint('')

                if 'info' in variables:
                    nprint("* Nodes Coordinates: ")
                    nprint(f"\tNode 1:", e=' ')
                    print_vector(e.nodes[0].coordinates, notation=0)
                    nprint(f"\tNode 2:", e=' ')
                    print_vector(e.nodes[1].coordinates, notation=0)
                    nprint('')

                    nprint("* Mechanical Properties: ")
                    nprint(f"\tYoung Modulus: {e.mechanical_prop.E}")
                    nprint(f"\tPoisson Ratio: {e.mechanical_prop.poisson}")
                    nprint('')

                    nprint("* Geometric Properties: ")
                    nprint(f"\tArea: {e.geometric_prop.area}")
                    nprint(f"\tInertia: {e.geometric_prop.inertia}")
                    nprint(f"\tLength: {e.length:.2f}")
                    nprint(f"\tInclination: {np.rad2deg(e.angle):.2f}°")
                    nprint('')

                    nprint("* Degrees of Freedom:", e=' ')
                    print_vector(e.equations, notation=0)
                    nprint('')
                    
                if 'fel' in variables:
                    nprint(f"* Load Vector:", e=' ')
                    print_vector(e.fel)
                    nprint('')
                
                if 'uel' in variables:
                    nprint(f"* Displacement:", e=' ')
                    print_vector(e.uel)
                    nprint('')

                if 'kel' in variables:
                    nprint("* Stiffness Matrix: ")
                    print_matrix(e.kel)
                    nprint('')

                if 'rot' in variables:
                    nprint("* Rotation Matrix: ")
                    print_matrix(e.rotation_matrix)

                if 'sol'in variables:
                    nprint(f"* Solution:", e=' ')
                    print_vector(e.solution)
                    nprint('')

                nprint(f"{'-'*21} *** {'-'*21}")

        def curry(func, f): return lambda text, e='\n': func(text, file=f, end=e)
        
        if file:
            with open(file, 'w') as f:
                nprint = curry(print, f)
                print_reults(f)
        else:
            nprint = curry(print, file)
            print_reults(file)