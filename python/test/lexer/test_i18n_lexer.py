import unittest

from gherkin.lexer.i18n_lexer import I18nLexer
from gherkin.sexp_recorder import SexpRecorder

class TestI18nLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = I18nLexer(SexpRecorder())

    def test_store_language_of_last_scanned_feature(self):
        self.lexer.scan('# language: fr\n')
        assert self.lexer.i18n_language.iso_code == 'fr'
        self.lexer.scan('# language: no\n')
        assert self.lexer.i18n_language.iso_code == 'no'

    def test_detect_language_when_there_are_spaces_and_crlf(self):
        self.lexer.scan('# language: da \r\n')
        assert self.lexer.i18n_language.iso_code == 'da'

    def test_detect_language_when_language_comment_is_not_first_line(self):
        self.lexer.scan("# hello\n# language: no\n")
        assert self.lexer.i18n_language.iso_code == 'no'

    def test_detect_language_when_language_is_on_third_line_with_empty_lines_above(self):
        self.lexer.scan("# hello\n\n# language: no\n")
        assert self.lexer.i18n_language.iso_code == 'no'

    def test_should_use_english_i18n_by_default(self):
        self.lexer.scan('Feature: foo\n')
        assert self.lexer.i18n_language.iso_code == 'en'
