from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast


class ConstructorInitialization(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, ConstructorInitializationAnalyzer())


class ConstructorInitializationAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.currentFunc = ''
        self.hasConstructor = False

    def visit_FunctionDef(self, node):
        if node.parent and not isinstance(node.parent, ast.FunctionDef):
            self.currentFunc = node.name

        if '__init__' == node.name and isinstance(node.parent, ast.ClassDef):
            # check constructor initialization
            # print('constructor initialization')
            if 'test' in node.parent.name.lower():
                self.hasConstructor = True

        self.generic_visit(node)

    def has_smell(self):
        return self.hasConstructor
