from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast

class MagicNumber(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, MagicNumberAnalyzer())


class MagicNumberAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.currentFunc = ''
        self.hasMagicNumber = False

    def visit_FunctionDef(self, node):
        if node.parent and not isinstance(node.parent, ast.FunctionDef):
            self.currentFunc = node.name
        self.generic_visit(node)

    def visit_Assert(self, node):
        self.check_magic_number(node.test)
        self.generic_visit(node)

    def check_magic_number(self, node):
        if isinstance(node, ast.Compare):  # For situations like `assert foo == 1`
            for comparator in node.comparators:
                if isinstance(comparator, ast.Constant) and isinstance(comparator.value, (int, float)) and not isinstance(comparator.value, bool):
                    self.hasMagicNumber = True
        elif isinstance(node, ast.Call):  # For situations like `assert UTC.utcoffset(None) == datetime.timedelta(0)`
            for arg in node.args:
                print(ast.unparse(node), type(arg))
                if isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)) and not isinstance(arg.value, bool):
                    self.hasMagicNumber = True

        for child in ast.iter_child_nodes(node):  # Recursively check other nodes
            self.check_magic_number(child)

    def visit_Attribute(self, node):
        # check if node.parent has args and if the parent is an assert statement.
        if hasattr(node.parent, 'args') and 'assert' in ast.unparse(node.parent).lower():
            args = node.parent.args
            for arg in args:
                if isinstance(arg, ast.Constant):
                    if isinstance(arg.value, (int, float, complex)) and not isinstance(arg.value, bool):
                        self.hasMagicNumber = True
                elif isinstance(node, ast.Call):  # For situations like `assertEqual(foo, 1)`
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)):
                            self.hasMagicNumber = True
        self.generic_visit(node)

    def has_smell(self):

        return self.hasMagicNumber