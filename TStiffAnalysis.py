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
    _nodes_list: list[TStiffNode] = field(init=False, default_factory=list)
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
                if not any(id(n) == id(node) for n in self.nodes_list):
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
                    node.DoF[3] = self.number_equations
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
        index = 0

        for node in self.nodes_list:
            for spring in node.springs:
                spring_type, value = spring

                dof = node.DoF[spring_to_DoF[spring_type]]
                self.KG[dof, dof] += value

            index += 1
   
    def assemble(self, element:TStiffElement):
        pass

    def Run(self)->None:
        self.check_for_prescribed_displacements()

        for element in self.elements:
            element.rotate()
            element.calc_stiff()

            self.assemble(element)

        self.check_for_prescribed_springs()

        # K00, F0 = self.get_free_equations()
        # K10, F1 = self.get_constrained_equations()

        # U0 = np.linalg.solve(K00, F0)

        # support_reaction_forces = K10@U0 + F1