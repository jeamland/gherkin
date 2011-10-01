import unittest

from nose import tools

from gherkin.lexer.exceptions import LexingError
from gherkin.lexer.ext.lexer_en import Lexer
from gherkin.sexp_recorder import SexpRecorder

class TestLexer(unittest.TestCase):
    def setUp(self):
        self.listener = SexpRecorder()
        self.lexer = Lexer(self.listener)

    def scan(self, data):
        self.lexer.scan(data)

    def check(self, expected):
        tools.eq_(self.listener.sexps, expected)

    def test_parse_a_one_line_comment(self):
        self.scan(u"# My comment\n")
        self.check([
            [u"comment", u"# My comment", 1],
            [u"eof"],
        ])

    def test_parse_a_multiline_comment(self):
        self.scan(u"# Hello\n\n# World\n")
        self.check([
            [u"comment", u"# Hello", 1],
            [u"comment", u"# World", 3],
            [u"eof"]
        ])

    def test_not_consume_comments_as_part_of_a_multiline_name(self):
        self.scan(u"Scenario: test\n#hello\n Scenario: another")
        self.check([
            [u"scenario", u"Scenario", u"test", u"", 1],
            [u"comment", u"#hello", 2],
            [u"scenario", u"Scenario", u"another", u"", 3],
            [u"eof"]
        ])

    def test_not_consume_comments_as_part_of_a_multiline_example_name(self):
        self.scan(u"Examples: thing\n# ho hum\n| 1 | 2 |\n| 3 | 4 |\n")
        self.check([
            [u"examples", u"Examples", u"thing", u"", 1],
            [u"comment",  u"# ho hum", 2],
            [u"row", [u"1", u"2"], 3],
            [u"row", [u"3", u"4"], 4],
            [u"eof"]
        ])

    def test_allow_empty_comment_lines(self):
        self.scan(u"#\n   # A comment\n   #\n")
        self.check([
            [u"comment", u"#", 1],
            [u"comment", u"# A comment", 2],
            [u"comment", u"#", 3],
            [u"eof"]
        ])

    @tools.raises(LexingError)
    def test_not_allow_comments_within_the_feature_description(self):
        self.scan(u"Feature: something\nAs a something\n# Comment\nI want something")