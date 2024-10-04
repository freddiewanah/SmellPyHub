from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast

class SuboptimalAssert(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, SuboptimalAssertAnalyzer())


class SuboptimalAssertAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.currentFunc = ''
        self.hasSuboptimal = False

    def visit_FunctionDef(self, node):
        if node.parent and not isinstance(node.parent, ast.FunctionDef):
            self.currentFunc = node.name
        self.generic_visit(node)

    def visit_Assert(self, node):

        if 'assert True' in ast.unparse(node) or 'assert False' in ast.unparse(node):
            self.hasSuboptimal = True
        # if ast.unparse(node.test).endswith('is True') or ast.unparse(node.test).endswith('is False'):
        #     self.hasSuboptimal = True
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if 'assert' in node.attr and 'assertRaises' not in node.attr:
            args = node.parent.args
            supFlag = False
            for arg in args:

                if ast.unparse(arg) == 'True' and 'asserttrue' not in node.attr.lower():
                    supFlag = True
                    break
                if ast.unparse(arg) == 'False' and 'assertfalse' not in node.attr.lower():
                    supFlag = True
                    break
                if ast.unparse(arg) == 'None' and (
                        'assertisnone' not in node.attr.lower() and 'assertisnotnone' not in node.attr.lower()):
                    supFlag = True
                    break
                if '>' in ast.unparse(arg) or '<' in ast.unparse(arg) or '>=' in ast.unparse(
                        arg) or '<=' in ast.unparse(arg) or '==' in ast.unparse(arg):
                    if 'assertless' not in node.attr.lower() and 'assertgreater' not in node.attr.lower() and 'equal' not in node.attr.lower() and 'assertnotequal' not in node.attr.lower():
                        supFlag = True
                        break
                if ' is not ' in ast.unparse(arg) or ' is ' in ast.unparse(arg):
                    if 'assertis' not in node.attr.lower() and 'assertisnot' not in node.attr.lower() and (
                            'true' in node.attr.lower() or 'false' in node.attr.lower()) and args.index(arg) == 0:
                        supFlag = True
                        break

                if (' in ' in ast.unparse(arg) or ' not in ' in ast.unparse(arg)) and (
                        'for ' not in ast.unparse(arg) or 'lambda ' not in ast.unparse(arg)):
                    if 'assertin' not in node.attr.lower() and 'assertnotin' not in node.attr.lower() and (
                            'true' in node.attr.lower() or 'false' in node.attr.lower()) and args.index(arg) == 0:
                        supFlag = True
                        break
            if supFlag:
                self.hasSuboptimal = True

        self.generic_visit(node)

    def has_smell(self):
        return self.hasSuboptimal