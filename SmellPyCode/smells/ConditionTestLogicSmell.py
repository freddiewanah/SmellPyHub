from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast

class ConditionTestLogic(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, ConditionTestLogicAnalyzer())


class ConditionTestLogicAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.currentFunc = ''
        self.hasCondition = False

    def iter_fields(self, node):
        """
        Yield a tuple of ``(fieldname, value)`` for each field in ``node._fields``
        that is present on *node*.
        """
        for field in node._fields:
            try:
                yield field, getattr(node, field)
            except AttributeError:
                pass
    def _check_assign(self, node):
        currentNode = node
        # print(ast.unparse(node))
        flag = False
        for field, value in self.iter_fields(node):
            # if value:
            #     print(field, value, ast.unparse(value))
            if field == 'iter' or field == 'ifs':
                return True
            if field == 'generators' and  value:
                flag = self._check_assign(value[0])
            if isinstance(value, ast.Call):
                # check the parameters of the call
                for arg in value.args:
                    if isinstance(arg, ast.GeneratorExp):
                        flag = self._check_assign(arg)
            if (isinstance(value, ast.SetComp) or isinstance(value, ast.ListComp) or isinstance(value, ast.DictComp)) and field == 'value':
                flag = self._check_assign(value)

        return flag

    def _check_if(self, node):
        currentNode = node
        while currentNode.parent is not None:
            currentNode = currentNode.parent
            if isinstance(currentNode, ast.If) or isinstance(currentNode, ast.While) or isinstance(currentNode, ast.For):
                return True
        return False

    def visit_FunctionDef(self, node):
        if node.parent and not isinstance(node.parent, ast.FunctionDef) and 'test' in node.name.lower():
            self.currentFunc = node.name
        self.generic_visit(node)


    def visit_If(self, node):
        if 'test' in self.currentFunc.lower() or self.currentFunc[0] == '_':
            self.hasCondition = True
        self.generic_visit(node)

    def visit_While(self, node):
        if 'test' in self.currentFunc.lower() or self.currentFunc[0] == '_':
            self.hasCondition = True
        self.generic_visit(node)

    def visit_For(self, node):
        if 'test' in self.currentFunc.lower() or self.currentFunc[0] == '_':
            self.hasCondition = True
        self.generic_visit(node)

    def visit_Assign(self, node):
        if 'test' in self.currentFunc.lower() or (self.currentFunc and self.currentFunc[0] == '_'):
            if self._check_assign(node):
                self.hasCondition = True
        self.generic_visit(node)

    def visit_ListComp(self, node):
        # Check list comprehensions which can have embedded for-loops
        self.hasCondition = True
        self.generic_visit(node)

    def visit_SetComp(self, node):
        # Check set comprehensions which can have embedded for-loops
        self.hasCondition = True
        self.generic_visit(node)

    def visit_DictComp(self, node):
        # Check dict comprehensions which can have embedded for-loops
        self.hasCondition = True
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if 'assert' in node.attr:
            if 'test' in self.currentFunc.lower() or self.currentFunc[0] == '_':
                if self._check_if(node):
                    self.hasCondition = True
        self.generic_visit(node)

    def has_smell(self):
        return self.hasCondition