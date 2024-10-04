from .GeneralSmellWithContent import GeneralSmellWithContent, GeneralAnalyzer
import ast


class IgnoredTest(GeneralSmellWithContent):
    def __init__(self, test_code):
        super().__init__(test_code, IgnoredTestAnalyzer())


class IgnoredTestAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.currentFunc = ''


    def has_smell(self, lines):
        hasIgnored = False
        tree = ast.parse('\n'.join(lines))
        if ('@unittest.skip' in ast.unparse(tree) and ('.skipUnless' not in ast.unparse(tree) and '.skipIf' not in ast.unparse(tree)) )or (' skipTest(' in ast.unparse(tree) and 'tf' in ast.unparse(tree)) or ('pytest.mark.skip' in ast.unparse(tree) and 'pytest.mark.skipif' not in ast.unparse(tree)):
            hasIgnored = True
        return hasIgnored
