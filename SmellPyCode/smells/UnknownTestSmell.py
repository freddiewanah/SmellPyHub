from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast


class UnknownTest(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, UnknownTestAnalyzer())


class UnknownTestAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.calledAttrs = {}
        self.setUpAttrs = []
        self.hasUnknownTest = False
        self.currentFunc = ''

    def visit_FunctionDef(self, node):
        if 'test' in node.name:
            # check if the function is not a fixture
            if '@pytest.fixture' not in ast.unparse(node):
                if 'assert' not in ast.unparse(node) and 'test' in node.name and node.name[0] != '_' and 'pytest.raises' not in ast.unparse(node) and 'pytest.deprecated_call' not in ast.unparse(node):
                    self.hasUnknownTest = True
        if '__init__' != node.name:
            self.generic_visit(node)

    def has_smell(self):
        return self.hasUnknownTest

