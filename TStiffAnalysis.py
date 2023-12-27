#%% --------------------------
#       IMPORTED MODULES
# ----------------------------
from dataclasses import dataclass, field 
from TStiffElement import TStiffElement
from TStiffNode import TStiffNode

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
    _number_free_equations: int = field(init=False)
    _number_equations: int = field(init=False)

    def calc_free_equations(self, count: int)-> int:
        for element in self._elements:
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

#%% --------------------------
#       CLASS METHODS
# ----------------------------
        """
        Concatenates every node in the structure, making sure it 
        only appears once
        """
            for node in element.nodes:
        """
        Find the total number of equations in the system and 
        the number of free equations used to solve the displacements
        """
        """
        Sets the degrees of freedom ('dof') in a given 'node'. 
        """
            """
            Calculates the number of free equations in the system
            """
                if node.support_type == 'Free':
                    node.DoF[0] = count
                    node.DoF[1] = count+1
                    node.DoF[2] = count+2
                    count += 3
                
                elif node.support_type == 'RollerX':
                    node.DoF[0] = count
                    node.DoF[2] = count+1
                    count+=2

                elif node.support_type == 'RollerY':
                    node.DoF[1] = count
                    node.DoF[2] = count+1
                    count+=2

                elif node.support_type == 'Pinned':
                    node.DoF[2] = count
                    count += 1

                if node.hinge:
                    node.DoF[3] = count
                    count += 1
            return count

    def calc_constrained_equations(self, count: int):
        for element in self._elements:
            for node in element.nodes:
            """
            Calculates the number of constrained equations in the system
            """
                if node.support_type == 'RollerX':
                    node.DoF[1] = count
                    count+=1

                elif node.support_type == 'RollerY':
                    node.DoF[0] = count
                    count+=1

                elif node.support_type == 'Pinned':
                    node.DoF[0] = count
                    node.DoF[1] = count+1
                    count+=2
                
                elif node.support_type == "Fixed":
                    node.DoF[0] = count
                    node.DoF[1] = count+1
                    node.DoF[2] = count+2
                    count+=3
            return count

    def find_DoF(self):
        count = 0
        count = self.calc_free_equations(count)

        self._number_free_equations = count
        
        count = self.calc_constrained_equations(count)
        self._number_equations = count