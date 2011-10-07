import mock
from nose import tools

from gherkin.lexer.exceptions import LexingError

from .support import LexerTest

class TestDocString(LexerTest):
    def scan_doc(self, content):
        self.scan(u'"""\n{}\n"""'.format(content))

    def setUp(self):
        super(TestDocString, self).setUp()
        self.doc_string = self.listener.doc_string = mock.Mock()

    def test_provide_the_amount_of_indentation_of_the_triple_quotes_to_the_listener(self):
        string = u'''Feature: some feature
  Scenario: some scenario
    Given foo
    """
      Hello
    Goodbye
    """
    Then bar
'''
        self.scan(string)
        self.doc_string.assert_called_with(u'', u"  Hello\nGoodbye", 4)

    def test_parse_a_simple_doc_string(self):
        self.scan_doc(u"I am a doc_string")
        self.doc_string.assert_called_with(u'', u"I am a doc_string", 1)

    def test_parse_an_empty_doc_string(self):
        self.scan(u"Feature: Hi\nScenario: Hi\nGiven a step\n\"\"\"\n\"\"\"")
        self.doc_string.assert_called_with(u'', u'', 4)

    def test_treat_a_string_containing_ony_newlines_as_only_newlines(self):
        self.scan_doc(u"\n\n")
        self.doc_string.assert_called_with(u'', u"\n\n", 1)

    def test_parse_content_separated_by_two_newlines(self):
        self.scan_doc(u"A\n\nB")
        self.doc_string.assert_called_with(u'', u"A\n\nB", 1)

    def test_parse_a_multiline_string(self):
        self.scan_doc(u"A\nB\nC\nD")
        self.doc_string.assert_called_with(u'', u"A\nB\nC\nD", 1)

    def test_ignore_unescaned_quotes_inside_the_string_delimiters(self):
        self.scan_doc(u'What does "this" mean?')
        self.doc_string.assert_called_with(u'', u'What does "this" mean?', 1)

    def test_preserve_whitespace_within_the_triple_quotes(self):
        string = u'''
    """
      Line one
 Line two
    """
'''[1:]
        self.scan(string)
        self.doc_string.assert_called_with(u'', u"  Line one\nLine two", 1)

    def test_preserve_tabs_within_the_content(self):
        self.scan_doc(u"I have\tsome tabs\nInside\t\tthe content")
        self.doc_string.assert_called_with(u'', u"I have\tsome tabs\nInside\t\tthe content", 1)

    def test_handle_complex_doc_strings(self):
        string = u'''
# Feature comment
@one
Feature: Sample

  @two @three
  Scenario: Missing
    Given missing

1 scenario (1 passed)
1 step (1 passed)

'''[1:]
        self.scan_doc(string)
        self.doc_string.assert_called_with(u'', string, 1)

    def test_allow_whitespace_after_the_closing_doc_string_delimiter(self):
        string = u'''
    """
      Line one
    """
'''[1:]
        self.scan(string)
        self.doc_string.assert_called_with(u'', u"  Line one", 1)

    def test_preserve_the_last_newlines_at_the_end_of_a_doc_string(self):
        string = u'''
     """
     DocString text


     """
'''[1:]
        self.scan(string)
        self.doc_string.assert_called_with(u'', u"DocString text\n\n", 1)

    def test_preserve_crlf_within_doc_strings(self):
        self.scan(u"\"\"\"\r\nLine one\r\nLine two\r\n\r\n\"\"\"")
        self.doc_string.assert_called_with(u'', u"Line one\r\nLine two\r\n", 1)

    def test_unescape_escaped_triple_quotes(self):
        string = u'''
    """
    \\"\\"\\"
    """
'''[1:]
        self.scan(string)
        self.doc_string.assert_called_with(u'', u'"""', 1)

    def test_not_unescape_escaped_single_quotes(self):
        string = u'''
    """
    \\" \\"\\"
    """
'''[1:]
        self.scan(string)
        self.doc_string.assert_called_with(u'', u'\\" \\"\\"', 1)

    def test_lex_doc_string_content_types(self):
        string = u'''
    """gherkin type
    Feature: Doc String Types
    """
'''[1:]
        self.scan(string)
        self.doc_string.assert_called_with(u'gherkin type', u'Feature: Doc String Types', 1)
