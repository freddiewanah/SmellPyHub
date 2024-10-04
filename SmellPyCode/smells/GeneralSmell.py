import os
import ast
class GeneralSmell:
    def __init__(self, test_code, analyzer):
        self.test_code = test_code
        self.tree = ast.parse(self.test_code)
        self.analyzer = analyzer

    def detect_smell(self):
        tree = self.tree
        tree.parent = None
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        self.analyzer.visit(tree)
        return self.analyzer.has_smell()


class GeneralAnalyzer(ast.NodeVisitor):
    def has_smell(self):
        raise NotImplementedError
