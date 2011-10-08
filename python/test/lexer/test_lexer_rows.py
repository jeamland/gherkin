# -*- coding: utf8 -*-

import mock
from nose import tools

from gherkin.lexer.exceptions import LexingError

from .support import LexerTest

class TestRows(LexerTest):
    def setUp(self):
        super(TestRows, self).setUp()
        self.comment = self.listener.comment = mock.Mock()
        self.row = self.listener.row = mock.Mock()

    def test_parse_rows_1(self):
        self.scan(u"|a|b|\n")
        self.row.assert_called_with(list(u'ab'), 1)

    def test_parse_rows_2(self):
        self.scan(u"|a|b|c|\n")
        self.row.assert_called_with(list(u'abc'), 1)

    def test_parse_a_row_with_many_cells(self):
        self.scan(u"|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|\n")
        self.row.assert_called_with(list(u'abcdefghijklmnop'), 1)

    def test_parse_multicharacter_cell_content(self):
        self.scan(u"| foo | bar |\n")
        self.row.assert_called_with([u'foo', u'bar'], 1)

    def test_escape_backslashed_pipes(self):
        self.scan(u'| \| | the | \a | \\ |   \|\\\|    |\n')
        self.row.assert_called_with([u'|', u'the', u'\a', u'\\', u'|\\|'], 1)

    def test_parse_cells_with_newlines(self):
        self.scan(u"|\\n|\n")
        self.row.assert_called_with([u"\n"], 1)

    def test_parse_cells_with_spaces_within_the_content(self):
        self.scan(u"| Dill pickle | Valencia orange |\n")
        self.row.assert_called_with([u"Dill pickle", u"Valencia orange"], 1)

    def test_allow_utf8_1(self):
        self.scan(u" | ůﻚ | 2 | \n")
        self.row.assert_called_with([u"\u016f\ufeda", u"2"], 1)

    def test_allow_utf8_2(self):
        self.scan(u"| 繁體中文  而且|並且| 繁體中文  而且|並且|\n")
        self.row.assert_called_with([u"\u7e41\u9ad4\u4e2d\u6587  \u800c\u4e14",
                                     u"\u4e26\u4e14",
                                     u"\u7e41\u9ad4\u4e2d\u6587  \u800c\u4e14",
                                     u"\u4e26\u4e14"], 1)

    def test_parse_a_2x2_table(self):
        self.scan(u"| 1 | 2 |\n| 3 | 4 |\n")
        tools.eq_(self.row.call_args_list, [
            (([u'1', u'2'], 1), {}),
            (([u'3', u'4'], 2), {}),
        ])

    def test_parse_a_2x2_table_with_empty_cells(self):
        self.scan(u"| 1 |  |\n|| 4 |\n")
        tools.eq_(self.row.call_args_list, [
            (([u'1', u''], 1), {}),
            (([u'', u'4'], 2), {}),
        ])

    def test_parse_a_row_with_empty_cells(self):
        self.scan(u"| 1 |  |\n")
        self.scan(u"|1||\n")
        tools.eq_(self.row.call_args_list, [
            (([u'1', u''], 1), {}),
            (([u'1', u''], 1), {}),
        ])

    def test_parse_a_1x2_table_that_does_not_end_in_a_newline(self):
        self.scan(u"| 1 | 2 |")
        self.row.assert_called_with(list(u'12'), 1)

    def test_parse_a_row_without_spaces_and_with_a_newline(self):
        self.scan(u"|1|2|\n")
        self.row.assert_called_with(list(u'12'), 1)

    def test_parse_a_row_with_whitespace_after_the_rows(self):
        self.scan("| 1 | 2 | \n ")
        self.row.assert_called_with(list(u'12'), 1)

    def test_parse_a_row_with_lots_of_whitespace(self):
        self.scan(u"  \t| \t   abc\t| \t123\t \t\t| \t\t   \t \t\n  ")
        self.row.assert_called_with([u"abc", u"123"], 1)

    def test_parse_a_table_with_a_commented_out_row(self):
        self.scan(u"|abc|\n#|123|\n|def|\n")
        self.comment.assert_called_with(u"#|123|", 2)
        tools.eq_(self.row.call_args_list, [
            (([u'abc'], 1), {}),
            (([u'def'], 3), {}),
        ])

    @tools.raises(LexingError)
    def test_raise_error_for_rows_that_are_not_closed_1(self):
        self.scan(u"|| oh hello \n")

    @tools.raises(LexingError)
    def test_raise_error_for_rows_that_are_followed_by_a_comment(self):
        self.scan(u"|hi| # oh hello \n")

    @tools.raises(LexingError)
    def test_raise_error_for_rows_that_are_not_closed_2(self):
        self.scan(u"|| oh hello \n  |Shouldn't Get|Here|")
