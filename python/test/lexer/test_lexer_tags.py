# -*- coding: utf8 -*-

import mock
from nose import tools

from gherkin.lexer.exceptions import LexingError

from .support import LexerTest

class TestTags(LexerTest):
    def setUp(self):
        super(TestTags, self).setUp()
        self.tag = self.listener.tag = mock.Mock()

    def test_lex_a_single_tag(self):
        self.scan(u"@dog\n")
        self.tag.assert_called_with(u"@dog", 1)

    def test_lex_multiple_tags(self):
        self.scan(u"@dog @cat\n")
        tools.eq_(len(self.tag.call_args_list), 2)

    def test_lex_utf8_tags(self):
        self.scan(u"@シナリオテンプレート\n")
        self.tag.assert_called_with(u"@シナリオテンプレート", 1)

    def test_lex_mixed_tags(self):
        self.scan(u"@wip @Значения\n")
        tools.eq_(self.tag.call_args_list, [
            ((u"@wip", 1), {}),
            ((u"@Значения", 1), {})
        ])

    def test_lex_wacky_identifiers(self):
        self.scan(u"@BJ-x98.77 @BJ-z12.33 @O_o @#not_a_comment\n")
        tools.eq_(len(self.tag.call_args_list), 4)

    def test_lex_tags_without_spaces_between_them(self):
        self.scan(u"@one@two\n")
        tools.eq_(len(self.tag.call_args_list), 2)

    @tools.raises(LexingError)
    def test_not_lex_tags_beginning_with_two_at_signs(self):
        self.scan(u"@@test\n")

    @tools.raises(LexingError)
    def test_not_lex_a_lone_at_sign(self):
        self.scan(u"@\n")
