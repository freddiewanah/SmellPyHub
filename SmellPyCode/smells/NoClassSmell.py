from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast


class NoClass(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, NoClassAnalyzer())


class NoClassAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.calledAttrs = {}
        self.setUpAttrs = []
        self.hasClass = False
        self.currentFunc = ''


    def visit_ClassDef(self, node):
        self.hasClass = True
        self.generic_visit(node)

    def visit_Import(self, node):
        # check if pytest is imported
        print("Import: ", ast.unparse(node))
        for alias in node.names:
            if alias.name == 'pytest':
                self.hasClass = True
        self.generic_visit(node)


    def has_smell(self):
        return not self.hasClass

