import os
import ast


class GeneralSmellWithContent:
    def __init__(self, test_code, analyzer):
        self.test_code = test_code
        self.tree = ast.parse(self.test_code)
        self.analyzer = analyzer

    def detect_smell(self):
        return self.analyzer.has_smell(self.test_code.split('\n'))


class GeneralAnalyzer(ast.NodeVisitor):
    def has_smell(self, lines):
        raise NotImplementedError
