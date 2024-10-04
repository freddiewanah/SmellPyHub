from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast

class DuplicateAssert(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, DuplicateAssertAnalyzer())


class DuplicateAssertAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.functions = {}
        self.currentFunc = ''


    def visit_FunctionDef(self, node):
        # print(ast.unparse(node))
        if node.parent and not isinstance(node.parent, ast.FunctionDef):
            self.currentFunc = node.name
        self.functions[self.currentFunc] = {}
        self.generic_visit(node)

    def visit_Assert(self, node):
        if len(self.functions[self.currentFunc]) != 0:
            self.functions[self.currentFunc].append(node)
        else:
            self.functions[self.currentFunc] = [node]
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if 'assert' in node.attr and 'test' in self.currentFunc:
            self.hasAssert = True
            print(ast.unparse(node))
            print(ast.unparse(node.parent))
            print(ast.unparse(node.parent.parent))
            if len(self.functions[self.currentFunc]) == 0:
                self.functions[self.currentFunc] = [node.parent]
            else:
                self.functions[self.currentFunc].append(node.parent)

        self.generic_visit(node)

    def has_smell(self):
        assertions = self.functions
        hasDuplicate = False
        for key in assertions.keys():
            if len(assertions[key]) > 1:
                for i in range(len(assertions[key]) - 1):
                    for j in range(i + 1, len(assertions[key])):
                        funcA = ast.unparse(assertions[key][i])
                        funcB = ast.unparse(assertions[key][j])
                        if funcA == funcB:
                            print(funcA, funcB, key, 'Duplicate Assert')
                            hasDuplicate = True
                            break
        return hasDuplicate