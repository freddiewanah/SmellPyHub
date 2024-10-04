from .GeneralSmellWithContent import GeneralSmellWithContent, GeneralAnalyzer
import ast


class MysteryGuest(GeneralSmellWithContent):
    def __init__(self, test_code):
        super().__init__(test_code, MysteryGuestAnalyzer())


class MysteryGuestAnalyzer(GeneralAnalyzer):
    def __init__(self):
        self.assert_count = 0
        self.assertArgs = []
        self.currentFunc = ''


    def has_smell(self, lines):
        hasGuest = any('open(' in line and ('\'r\'' in line or '\"r\"' in line) and 'mock' not in line for line in lines)
        return hasGuest
