from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast


class ExceptionHandling(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, ExceptionHandlingAnalyzer())


class ExceptionHandlingAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.hasException = False
        self.currentFunc = ''

    def visit_FunctionDef(self, node):
        if node.parent and not isinstance(node.parent, ast.FunctionDef):
            self.currentFunc = node.name
        self.generic_visit(node)

    def visit_Try(self, node):
        if 'raise' in ast.unparse(node) or 'assert' in ast.unparse(node):
            if 'test' in self.currentFunc.lower() or (self.currentFunc[0] == '_' and '__init__' not in self.currentFunc):
                self.hasException = True
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        if 'test' in self.currentFunc.lower() or (self.currentFunc[0] == '_' and '__init__' not in self.currentFunc):
            self.hasException = True
        self.generic_visit(node)

    def visit_Raise(self, node):
        if 'test' in self.currentFunc.lower() or (self.currentFunc[0] == '_' and '__init__' not in self.currentFunc):
            self.hasException = True
        self.generic_visit(node)

    def has_smell(self):
        return self.hasException
