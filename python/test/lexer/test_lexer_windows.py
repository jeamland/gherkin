from nose import tools

from gherkin.lexer.exceptions import LexingError

from .support import LexerTest

class TestBOM(LexerTest):
    def test_windows_file_with_bom_should_work_just_fine(self):
        self.scan_file("with_bom.feature")
        self.check([
            [u"feature", u"Feature", u"Feature Text", u"", 1],
            [u"scenario", u"Scenario", u"Reading a Scenario", u"", 2],
            [u"step", u"Given ", u"there is a step", 3],
            [u"eof"],
        ])