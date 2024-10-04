from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast


class FixtureAssert(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, FixtureAssertAnalyzer())


class FixtureAssertAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.hasFixtureAssert = False
        self.currentFunc = ''

    def visit_FunctionDef(self, node):
        if node.parent and not isinstance(node.parent, ast.FunctionDef):
            self.currentFunc = node.name
        self.generic_visit(node)

    def visit_Assert(self, node):
        if 'setUp' == self.currentFunc:
            self.hasFixtureAssert = True
        if 'pytest.fixture' in ast.unparse(node.parent):
            self.hasFixtureAssert = True
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if 'assert' in node.attr:
            if 'setUp' == self.currentFunc:
                self.hasFixtureAssert = True
            if 'pytest.fixture' in ast.unparse(node.parent.parent.parent):
                self.hasFixtureAssert = True

        self.generic_visit(node)




    def has_smell(self):
        return self.hasFixtureAssert
