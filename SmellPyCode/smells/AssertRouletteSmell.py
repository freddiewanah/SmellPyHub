from .GeneralSmell import GeneralSmell, GeneralAnalyzer
import ast

class AssertRoulette(GeneralSmell):
    def __init__(self, test_code):
        super().__init__(test_code, AssertRouletteAnalyzer())


class AssertRouletteAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.currentFunc = ''
        self.twoArgumentAssert = ["assertEqual", "assertNotEqual", "assertIs", "assertIsNot", "assertIn",
                                  "assertNotIn", "assertIsInstance", "assertNotIsInstance", "assertDictEqual",
                                    "assertDictContainsSubset", "assertGreater", "assertGreaterEqual", "assertLess",
                                    "assertLessEqual", "assertMultiLineEqual", "assertRegex", "assertNotRegex",
                                  ]
        self.oneArgumentAssert = ["assertTrue", "assertFalse", "assertIsNone", "assertIsNotNone"]
        self.threeArgumentAssert = ["assertAlmostEqual", "assertNotAlmostEqual", 'assertNear', 'assertBetween', 'assert_almost_equal', 'assertNDArrayNear']

    def visit_FunctionDef(self, node):
        if node.parent and not isinstance(node.parent, ast.FunctionDef):
            self.currentFunc = node.name
        self.generic_visit(node)

    def visit_Assert(self, node):
        self.assert_count += 1
        self.assertArgs.append([f'{self.currentFunc}:: ', node, 'Python Assert'])
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if 'assert' in node.attr:
            self.assert_count += 1
            self.assertArgs.append([f'{self.currentFunc}::{node.attr}', len(node.parent.args), ast.unparse(node.parent)])

        self.generic_visit(node)

    def has_smell(self):
        if self.assert_count == 1:
            return False
        hasAssertRoulette = False
        for assertArg in self.assertArgs:
            if 'Python Assert' in assertArg[2]:
                if assertArg[1].msg is None:
                    hasAssertRoulette = True
                    break
            else:
                key = assertArg[0]
                args = assertArg[1]

                currentName = key.split('::')[-1]
                if currentName in self.twoArgumentAssert:
                    if args == 2:
                        hasAssertRoulette = True
                        break
                elif currentName in self.oneArgumentAssert:
                    if args == 1:
                        hasAssertRoulette = True
                        break
                elif currentName in self.threeArgumentAssert:
                    if args == 3:
                        hasAssertRoulette = True
                        break
        return hasAssertRoulette