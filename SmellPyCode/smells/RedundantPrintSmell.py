from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast


class RedundantPrint(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, RedundantPrintAnalyzer())


class RedundantPrintAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.hasPrint = False
        self.currentFunc = ''

    def visit_FunctionDef(self, node):
        if node.parent and not isinstance(node.parent, ast.FunctionDef):
            self.currentFunc = node.name
        self.generic_visit(node)

    def visit_Call(self, node):

        if isinstance(node.func, ast.Name) and node.func.id == 'print' and 'test' in self.currentFunc.lower():
            self.hasPrint = True
        self.generic_visit(node)

    def has_smell(self):
        return self.hasPrint
