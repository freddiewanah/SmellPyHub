from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast


class SleepyTest(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, SleepyTestAnalyzer())


class SleepyTestAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.hasSleep = False
        self.currentFunc = ''

    def visit_FunctionDef(self, node):
        if node.parent and not isinstance(node.parent, ast.FunctionDef):
            self.currentFunc = node.name
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if 'sleep' in node.attr:
            self.hasSleep = True

        self.generic_visit(node)

    def has_smell(self):
        return self.hasSleep
