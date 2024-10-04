from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast


class DefaultTest(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, DefaultTestAnalyzer())


class DefaultTestAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.hasConstructor = False

    def visit_ClassDef(self, node):
        if 'mytestcase' in node.name.lower():
            self.hasConstructor = True


    def has_smell(self):
        return self.hasConstructor
