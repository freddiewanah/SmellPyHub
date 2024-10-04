from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast

class EagerTest(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, EagerTestAnalyzer())


class EagerTestAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assertArgs = []
        self.called_methods = set()
        self.assert_count = 0
        self.currentFunc = ''
        self.related_methods = set()
        self.variables = dict()  #

    def visit_FunctionDef(self, node):
        if node.parent and not isinstance(node.parent, ast.FunctionDef):
            self.currentFunc = node.name
        self.generic_visit(node)

    def visit_Assign(self, node):
        # if the assigned value is a method call, track its source method
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.variables[target.id] = node.value.func.attr
        self.generic_visit(node)
    def visit_Assert(self, node):
        self.assert_count += 1
        self.visit_Assert_Args(node.test)
        self.generic_visit(node)

    def visit_Assert_Args(self, node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            #print the node name
            if len(self.variables)<1 or ast.unparse(node.func.value).split('[')[0] in self.variables:
                self.related_methods.add(node.func.attr)
        if isinstance(node, ast.Name):
            # if this name is a variable we're tracking, add its source method
            if node.id in self.variables:
                self.called_methods.add(node.id)
                self.related_methods.add(self.variables[node.id])

        # Visit child nodes recursively
        for child in ast.iter_child_nodes(node):
            self.visit_Assert_Args(child)


    def visit_Attribute(self, node):
        if 'assert' in node.attr:
            self.assert_count += 1
            args = node.parent.args
            for arg in args:
                # print(ast.unparse(arg))
                # print(type(arg))
                if isinstance(arg, ast.Call):
                    if isinstance(arg.func, ast.Attribute):
                        if len(self.variables) < 1 or ast.unparse(arg.func.value).split('[')[0] in self.variables:
                            self.related_methods.add(arg.func.attr)
                if isinstance(arg, ast.Attribute):
                    if len(self.variables) < 1 or ast.unparse(arg.value).split('[')[0] in self.variables:
                        self.related_methods.add(arg.attr)
                if isinstance(arg, ast.Name):
                    # if this name is a variable we're tracking, add its source method
                    if arg.id in self.variables:
                        self.called_methods.add(arg.id)
                        self.related_methods.add(self.variables[arg.id])

        self.generic_visit(node)

    def has_smell(self):
        # print(self.called_methods)
        # print(self.related_methods)
        if len(self.called_methods) <=1:
            return False
        return self.assert_count > 1 and len(self.related_methods) > 1

    # Detection Logic in has_smell: Your final smell detection logic—checking if there's more than one assertion and if these assertions involve more than one related method—is a good starting point. However, the definition of an "Eager Test" might require a more nuanced approach. For instance, multiple assertions against the same method's output under different conditions might not constitute an "Eager Test" smell if they're conceptually part of the same test scenario.