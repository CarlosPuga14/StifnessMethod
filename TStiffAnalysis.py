from dataclasses import dataclass, field 
from TStiffElement import TStiffElement

@dataclass
class TStiffAnalysis:
    _elements: list[TStiffElement]
    _number_free_equations: int = field(init=False)
    _number_equations: int = field(init=False)

    def calc_free_equations(self, count: int)-> int:
        for element in self._elements:
            for node in element.nodes:
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