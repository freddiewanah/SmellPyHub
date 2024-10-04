from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast


class TestMaverick(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, TestMaverickAnalyzer())


class TestMaverickAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.calledAttrs = {}
        self.setUpAttrs = []
        self.fixtureNames = []
        self.hasMaverick = False
        self.currentFunc = ''

    def visit_Assign(self, node):
        if 'setUp' in self.currentFunc:
            target = node.targets[0]
            if 'self.' in ast.unparse(target).replace('cls.', 'self.'):
                if ', ' not in ast.unparse(target):
                    self.setUpAttrs.append(ast.unparse(target).replace('cls.', 'self.'))
                else:
                    targets = ast.unparse(target).replace('(', '').replace(')', '').split(', ')
                    for t in targets:
                        self.setUpAttrs.append(t.replace('cls.', 'self.'))
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if node.parent and not isinstance(node.parent, ast.FunctionDef):
            self.currentFunc = node.name
        if 'test' in node.name.lower():
            self.calledAttrs[node.name]= []

            # Detect pytest fixtures
        if any('@pytest.fixture' in ast.unparse(decorator) for decorator in node.decorator_list):
            self.fixtureNames.append(node.name)


        elif node.name != 'setUp' and len(self.setUpAttrs) != 0 and 'test' in node.name.lower():
            # check Test Maverick
            maverickFlag = False
            for attr in self.setUpAttrs + self.fixtureNames:
                if attr in ast.unparse(node):
                    maverickFlag = True
                    break
            if not maverickFlag:
                self.hasMaverick = True
        self.generic_visit(node)


    def has_smell(self):
        return self.hasMaverick

