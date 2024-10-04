from .GeneralSmellWithContent import GeneralSmellWithContent, GeneralAnalyzer
import ast


class ResourceOptimism(GeneralSmellWithContent):
    def __init__(self, test_code):
        super().__init__(test_code, ResourceOptimismAnalyzer())


class ResourceOptimismAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.currentFunc = ''


    def has_smell(self, lines):
        hasResourceOptimism = False
        hasGuest = any('open(' in line and ('\'r\'' in line or '\"r\"' in line) and 'mock' not in line for line in lines)
        if hasGuest:
            breakIndex = 0
            hasResourceOptimism = True
            for line in lines:
                if breakIndex == 1:
                    break
                if 'open(' in line and ('\'r\'' in line or '\"r\"' in line):
                    breakIndex = 1
                if 'isfile(' in line or 'exists(' in line or 'tempfile.' in line or 'NamedTemporaryFile' in line or 'tmpfile.' in line or 'mkdtemp(' in line or 'mkstemp(' in line:
                    hasResourceOptimism = False
                    break

        return hasResourceOptimism
