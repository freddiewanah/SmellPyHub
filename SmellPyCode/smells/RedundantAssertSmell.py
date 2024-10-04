from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast

class RedundantAssert(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, RedundantAssertAnalyzer())


class RedundantAssertAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.currentFunc = ''
        self.hasRedundant = False

    def visit_FunctionDef(self, node):
        if node.parent and not isinstance(node.parent, ast.FunctionDef):
            self.currentFunc = node.name
        self.generic_visit(node)

    def visit_Assert(self, node):
        sentence = ast.unparse(node).lower().replace('assert', '').replace(' ', '')
        if '==' in sentence:
            params = sentence.split('==')
            if params[1] == params[0]:
                self.hasRedundant = True
        sentence = ast.unparse(node).lower().replace(' ', '')
        if 'asserttrue' == sentence or 'assertfalse' == sentence:
            self.hasRedundant = True
        if sentence.startswith('asserttrue') or sentence.startswith('assertfalse'):
            self.hasRedundant = True
        self.generic_visit(node)


    def visit_Attribute(self, node):
        if 'assert' in node.attr:
            args = node.parent.args
            thisCall = node.parent
            temp = []
            count = 0
            if len(args) > 1 and ast.unparse(args[0]) == ast.unparse(args[1]):
                self.hasRedundant = True

            sentence = ast.unparse(thisCall).lower().replace(' ', '')
            if 'asserttrue(true)' in sentence or 'assertfalse(false)' in sentence:
                self.hasRedundant = True

        self.generic_visit(node)

    def has_smell(self):
        return self.hasRedundant