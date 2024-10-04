from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast


class GeneralFixture(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, GeneralFixtureAnalyzer())


class GeneralFixtureAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.calledAttrs = {}
        self.setUpAttrs = []
        self.currentFunc = ''
        self.fixtureNames = []

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
        if any('@pytest.fixture' in ast.unparse(decorator) for decorator in node.decorator_list):
            self.fixtureNames.append(node.name)
        if 'test' in node.name.lower():
            self.calledAttrs[node.name]= []
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if 'self.' in ast.unparse(node) and 'assert' not in ast.unparse(node) and self.currentFunc != 'setUp' and 'test' in self.currentFunc.lower():
            if self.currentFunc in self.calledAttrs.keys():
                self.calledAttrs[self.currentFunc].append(ast.unparse(node))
            else:
                self.calledAttrs[self.currentFunc] = [ast.unparse(node)]

        self.generic_visit(node)

    def has_smell(self):
        attrFlag = False
        # print(self.calledAttrs)
        # print(self.setUpAttrs)
        for key in self.calledAttrs.keys():
            for it in self.setUpAttrs:
                if it not in self.calledAttrs[key]:
                    # print("General Fixture")
                    attrFlag = True
                    break
            if attrFlag:
                break
        for key in self.fixtureNames:
            if key not in self.calledAttrs.keys():
                # print("General Fixture")
                attrFlag = True
                break
        return attrFlag
