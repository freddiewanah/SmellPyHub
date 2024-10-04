from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast

class ObscureInlineSetup(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, ObscureInlineSetupAnalyzer())


class ObscureInlineSetupAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.currentFunc = ''
        self.otherAttrs = {}
        self.fixtureNames = []

    def visit_FunctionDef(self, node):
        if node.parent and not isinstance(node.parent, ast.FunctionDef):
            self.currentFunc = node.name
        if any('@pytest.fixture' in ast.unparse(decorator) for decorator in node.decorator_list):
            self.fixtureNames.append(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        if 'setUp' not in self.currentFunc and 'test' in self.currentFunc.lower():
            for target in node.targets:
                func = self.currentFunc
                targetName = ast.unparse(target)
                if func not in self.fixtureNames:
                    if func in self.otherAttrs.keys():
                        if targetName not in self.otherAttrs[func]:
                            self.otherAttrs[func].append(targetName)
                    else:
                        self.otherAttrs[func] = [target]

        self.generic_visit(node)

    def has_smell(self):
        hasObscure = False
        for key in self.otherAttrs.keys():
            if len(self.otherAttrs[key]) >= 10:
                hasObscure = True
        return hasObscure