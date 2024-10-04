from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast


class EmptyTest(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, EmptyTestAnalyzer())


class EmptyTestAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.hasEmptyBody = False
        self.currentFunc = ''

    def visit_FunctionDef(self, node):
        if node.parent and not isinstance(node.parent, ast.FunctionDef):
            self.currentFunc = node.name
        if isinstance(node.body[0], ast.Pass) and 'test' in node.name.lower():
            # empty test
            # print('empty body')
            self.hasEmptyBody = True
        self.generic_visit(node)

    def has_smell(self):
        return self.hasEmptyBody
