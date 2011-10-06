import os.path
import unittest

from nose import tools

from gherkin.lexer.exceptions import LexingError
from gherkin.lexer.ext.lexer_en import Lexer
from gherkin.sexp_recorder import SexpRecorder

class LexerTest(unittest.TestCase):
    def setUp(self):
        self.listener = SexpRecorder()
        self.lexer = Lexer(self.listener)

    def scan(self, data):
        self.lexer.scan(data)

    def scan_file(self, filename):
        path = os.path.dirname(__file__)
        filename = os.path.join(path, '..', '..', '..', 'spec', 'gherkin',
                                'fixtures', filename)
        self.lexer.scan(open(filename).read())

    def check(self, sexps):
        for have, expected in zip(self.listener.sexps, sexps):
            tools.eq_(have, expected)

class TestComments(LexerTest):
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

class TestTags(LexerTest):
    def test_not_take_the_tags_as_part_of_a_multiline_name_feature_element(self):
        self.scan(u"Feature: hi\n Scenario: test\n\n@hello\n Scenario: another")
        self.check([
            [u"feature", u"Feature", u"hi", u"", 1],
            [u"scenario", u"Scenario", u"test", u"", 2],
            [u"tag", u"@hello", 4],
            [u"scenario", u"Scenario", u"another", u"", 5],
            [u"eof"],
        ])

class TestBackground(LexerTest):
    def test_allow_an_empty_background_name_and_description(self):
        self.scan(u"Background:\nGiven I am a step\n")
        self.check([
            [u"background", u"Background", u"", u"", 1],
            [u"step", u"Given ", u"I am a step", 2],
            [u"eof"],
        ])

    def test_allow_an_empty_background_description(self):
        self.scan(u"Background: Yeah\nGiven I am a step\n")
        self.check([
            [u"background", u"Background", u"Yeah", u"", 1],
            [u"step", u"Given ", u"I am a step", 2],
            [u"eof"],
        ])

    def test_allow_multiline_descriptions_ending_at_eof(self):
        self.scan(u"Background: I have several\n   Lines to look at\n   None starting with Given")
        self.check([
            [u"background", u"Background", u"I have several", u" Lines to look at\n None starting with Given", 1],
            [u"eof"],
        ])

    def test_allow_multiline_descriptions_including_whitespace(self):
        self.scan(u"""Feature: Hi
Background: It is my ambition to say 
  in ten sentences
    what others say 
  in a whole book.
Given I am a step""")
        self.check([
            [u"feature", u"Feature", u"Hi", u"", 1],
            [u"background", u"Background", u"It is my ambition to say", u"in ten sentences\n  what others say \nin a whole book.",2],
            [u"step", u"Given ", u"I am a step", 6],
            [u"eof"],
        ])

class TestScenarios(LexerTest):
    def test_scenario_parsed(self):
        self.scan(u"Scenario: Hello\n")
        self.check([
            [u"scenario", u"Scenario", u"Hello", u"", 1],
            [u"eof"],
        ])

    def test_allow_whitespace_lines_after_the_scenario_line(self):
        self.scan(u"""Scenario: bar

              Given baz
              """)
        self.check([
            [u"scenario", u"Scenario", u"bar", u"", 1],
            [u"step", u"Given ", u"baz", 3],
            [u"eof"],
        ])

    def test_allow_multiline_descriptions_including_whitespace(self):
        self.scan(u"""Scenario: It is my ambition to say
  in ten sentences
  what others say 
      in a whole book.
  Given I am a step
""")
        self.check([
            [u"scenario", u"Scenario", u"It is my ambition to say", u"in ten sentences\nwhat others say \n    in a whole book.", 1],
            [u"step", u"Given ", u"I am a step", 5],
            [u"eof"],
        ])

    def test_allow_multiline_names_ending_at_eof(self):
        self.scan(u"Scenario: I have several\nLines to look at\n None starting with Given")
        self.check([
            [u"scenario", u"Scenario", u"I have several", u"Lines to look at\nNone starting with Given", 1],
            [u"eof"],
        ])

    def test_ignore_gherkin_keywords_embedded_in_other_words(self):
        self.scan(u"""Scenario: I have a Button
Buttons are great
Given I have some
But I might not because I am a Charles Dickens character
""")
        self.check([
            [u"scenario", u"Scenario", u"I have a Button", u"Buttons are great", 1],
            [u"step", u"Given ", u"I have some", 3],
            [u"step", u"But ", u"I might not because I am a Charles Dickens character", 4],
            [u"eof"],
        ])

    def test_allow_step_keywords_in_scenario_names(self):
        self.scan(u"""Scenario: When I have when in scenario
I should be fine
Given I am a step
""")
        self.check([
            [u"scenario", u"Scenario", u"When I have when in scenario", u"I should be fine", 1],
            [u"step", u"Given ", u"I am a step", 3],
            [u"eof"],
        ])

class TestScenarioOutlines(LexerTest):
    def test_scenario_outline_is_parsed(self):
        self.scan(u"""Scenario Outline: Hello
  With a description
  Given a <what> cucumber
  Examples: With a name
    and a description
    |what|
    |green|
""")
        self.check([
            [u"scenario_outline", u"Scenario Outline", u"Hello", u"With a description", 1],
            [u"step", u"Given ", u"a <what> cucumber", 3],
            [u"examples", u"Examples", u"With a name", u"and a description", 4],
            [u"row", [u"what"], 6],
            [u"row", [u"green"], 7],
            [u"eof"],
        ])

    def test_parse_with_no_steps_or_examples(self):
        self.scan(u"""Scenario Outline: Hello

              Scenario: My Scenario
              """)
        self.check([
            [u"scenario_outline", u"Scenario Outline", u"Hello", u"", 1],
            [u"scenario", u"Scenario", u"My Scenario", u"", 3],
            [u"eof"],
        ])

    def test_allow_multiline_description(self):
        self.scan(u"""Scenario Outline: It is my ambition to say 
  in ten sentences
    what others say 
  in a whole book.
  Given I am a step
""")
        self.check([
            [u"scenario_outline", u"Scenario Outline", u"It is my ambition to say", u"in ten sentences\n  what others say \nin a whole book.", 1],
            [u"step", u"Given ", u"I am a step", 5],
            [u"eof"],
        ])

class TestExamples(LexerTest):
    def test_parse_example(self):
        self.scan(u"""Examples:
                               |x|y|
                               |5|6|
                               """)
        self.check([
            [u"examples", u"Examples", u"", u"", 1],
            [u"row", [u"x",u"y"], 2],
            [u"row", [u"5",u"6"], 3],
            [u"eof"],
        ])

    def test_parse_multiline_example_names(self):
        self.scan(u"""Examples: I'm a multiline name
and I'm ok
f'real
|x|
|5|
""")
        self.check([
            [u"examples", u"Examples", u"I'm a multiline name", u"and I'm ok\nf'real", 1],
            [u"row", [u"x"], 4],
            [u"row", [u"5"], 5],
            [u"eof"],
        ])

class TestSteps(LexerTest):
    def test_parse_steps_with_inline_table(self):
        self.scan(u"""Given I have a table
                               |a|b|
                               """)
        self.check([
            [u"step", u"Given ", u"I have a table", 1],
            [u"row", [u'a',u'b'], 2],
            [u"eof"],
        ])

    def test_parse_steps_with_inline_doc_string(self):
        self.scan(u"Given I have a string\n\"\"\"\nhello\nworld\n\"\"\"")
        self.check([
            [u"step", u"Given ", u"I have a string", 1],
            [u"doc_string", u'', u"hello\nworld", 2],
            [u"eof"],
        ])

class TestMiscellaneous(LexerTest):
    def test_find_the_feature_scenario_and_step(self):
        self.scan(u"Feature: Feature Text\n  Scenario: Reading a Scenario\n    Given there is a step\n")
        self.check([
            [u"feature", u"Feature", u"Feature Text", u"", 1],
            [u"scenario", u"Scenario", u"Reading a Scenario", u"", 2],
            [u"step", u"Given ", u"there is a step", 3],
            [u"eof"],
        ])

    def test_not_raise_an_error_when_whitespace_follows_the_feature(self):
        self.scan(u"Feature: Feature Text\n Scenario: Reading a Scenario\n    Given there is a step\n    ")
        self.check([
            [u"feature", u"Feature", u"Feature Text", u"", 1],
            [u"scenario", u"Scenario", u"Reading a Scenario", u"", 2],
            [u"step", u"Given ", u"there is a step", 3],
            [u"eof"],
        ])

    def test_find_the_feature_scenario_and_three_steps(self):
        self.scan(u"Feature: Feature Text\n  Scenario: Reading a Scenario\n    Given there is a step\n    And another step\n   And a third step\n")
        self.check([
            [u"feature", u"Feature", u"Feature Text", u"", 1],
            [u"scenario", u"Scenario", u"Reading a Scenario", u"", 2],
            [u"step", u"Given ", u"there is a step", 3],
            [u"step", u"And ", u"another step", 4],
            [u"step", u"And ", u"a third step", 5],
            [u"eof"],
        ])

    def test_find_feature_with_no_scenario(self):
        self.scan(u"Feature: Feature Text\n")
        self.check([
            [u"feature", u"Feature", u"Feature Text", u"", 1],
            [u"eof"],
        ])

    def test_parse_a_one_line_feature_with_no_newline(self):
        self.scan(u"Feature: hi")
        self.check([
            [u"feature", u"Feature", u"hi", u"", 1],
            [u"eof"],
        ])

    def test_find_multiline_feature_with_no_scenario(self):
        self.scan(u"Feature: Feature Text\n  And some more text")
        self.check([
            [u"feature", u"Feature", u"Feature Text", u"And some more text", 1],
            [u"eof"],
        ])

    def test_find_feature_with_scenario_but_no_steps(self):
        self.scan(u"Feature: Feature Text\nScenario: Reading a Scenario\n")
        self.check([
            [u"feature", u"Feature", u"Feature Text", u"", 1],
            [u"scenario", u"Scenario", u"Reading a Scenario", u"", 2],
            [u"eof"],
        ])

    def test_find_feature_and_two_scenarios(self):
        self.scan(u"Feature: Feature Text\nScenario: Reading a Scenario\n  Given a step\n\nScenario: A second scenario\n Given another step\n")
        self.check([
            [u"feature", u"Feature", u"Feature Text", u"", 1],
            [u"scenario", u"Scenario", u"Reading a Scenario", u"", 2],
            [u"step", u"Given ", u"a step", 3],
            [u"scenario", u"Scenario", u"A second scenario", u"", 5],
            [u"step", u"Given ", u"another step", 6],
            [u"eof"],
        ])

    def test_find_feature_and_two_scenarios_without_indentation(self):
        self.scan(u"Feature: Feature Text\nScenario: Reading a Scenario\nGiven a step\nScenario: A second scenario\nGiven another step\n")
        self.check([
            [u"feature", u"Feature", u"Feature Text", u"", 1],
            [u"scenario", u"Scenario", u"Reading a Scenario", u"", 2],
            [u"step", u"Given ", u"a step", 3],
            [u"scenario", u"Scenario", u"A second scenario", u"", 4],
            [u"step", u"Given ", u"another step", 5],
            [u"eof"],
        ])

    def test_find_things_in_the_proper_order(self):
        self.scan_file("simple_with_comments.feature")
        self.check([
            [u"comment", u"# Here is a comment", 1],
            [u"feature", u"Feature", u"Feature Text", u"", 2],
            [u"comment", u"# Here is another # comment", 3],
            [u"scenario", u"Scenario", u"Reading a Scenario", u"", 4],
            [u"comment", u"# Here is a third comment", 5],
            [u"step", u"Given ", u"there is a step", 6],
            [u"comment", u"# Here is a fourth comment", 7],
            [u"eof"],
        ])

    def test_support_comments_in_tables(self):
        self.scan_file("comments_in_table.feature")
        self.check([
            [u"feature", u"Feature", u"x", u"", 1],
            [u"scenario_outline", u"Scenario Outline", u"x", u"", 3],
            [u"step", u"Then ", u"x is <state>", 4],
            [u"examples", u"Examples", u"", u"", 6],
            [u"row", [u"state"], 7],
            [u"comment", u"# comment", 8],
            [u"row", [u"1"], 9],
            [u"eof"],
        ])

    def test_find_things_in_the_proper_order_with_tags_everywhere(self):
        self.scan_file("simple_with_tags.feature")
        self.check([
            [u"comment", u"# FC", 1],
            [u"tag", u"@ft",2],
            [u"feature", u"Feature", u"hi", u"", 3],
            [u"tag", u"@st1", 5],
            [u"tag", u"@st2", 5],
            [u"scenario", u"Scenario", u"First", u"", 6],
            [u"step", u"Given ", u"Pepper", 7],
            [u"tag", u"@st3", 9],
            [u"tag", u"@st4", 10],
            [u"tag", u"@ST5", 10],
            [u"tag", u"@#^%&ST6**!", 10],
            [u"scenario", u"Scenario", u"Second", u"", 11],
            [u"eof"],
        ])

    def test_lex_complicated_thing(self):
        self.scan_file("1.feature")
        self.check([
            [u"feature", u"Feature", u"Logging in", u"So that I can be myself", 1],
            [u"comment", u"# Comment", 3],
            [u"scenario", u"Scenario", u"Anonymous user can get a login form.", u"Scenery here", 4],
            [u"tag", u"@tag", 7],
            [u"scenario", u"Scenario", u"Another one", u"", 8],
            [u"eof"],
        ])

    def test_find_things_in_the_right_order_in_a_complex_feature(self):
        self.scan_file("complex.feature")
        self.check([
            [u"comment", u"#Comment on line 1", 1],
            [u"comment", u"#Comment on line 2", 2],
            [u"tag", u"@tag1", 3],
            [u"tag", u"@tag2", 3],
            [u"feature", u"Feature", u"Feature Text", u"In order to test multiline forms\nAs a ragel writer\nI need to check for complex combinations", 4],
            [u"comment", u"#Comment on line 9", 9],
            [u"comment", u"#Comment on line 11", 11],
            [u"background", u"Background", u"", u"", 13],
            [u"step", u"Given ", u"this is a background step", 14],
            [u"step", u"And ", u"this is another one", 15],
            [u"tag", u"@tag3", 17],
            [u"tag", u"@tag4", 17],
            [u"scenario", u"Scenario", u"Reading a Scenario", u"", 18],
            [u"step", u"Given ", u"there is a step", 19],
            [u"step", u"But ", u"not another step", 20],
            [u"tag", u"@tag3", 22],
            [u"scenario", u"Scenario", u"Reading a second scenario", u"With two lines of text", 23],
            [u"comment", u"#Comment on line 24", 25],
            [u"step", u"Given ", u"a third step with a table", 26],
            [u"row", [u"a", u"b"], 27],
            [u"row", [u"c", u"d"], 28],
            [u"row", [u"e", u"f"], 29],
            [u"step", u"And ", u"I am still testing things", 30],
            [u"row", [u"g", u"h"], 31],
            [u"row", [u"e", u"r"], 32],
            [u"row", [u"k", u"i"], 33],
            [u"row", [u'n', u''], 34],
            [u"step", u"And ", u"I am done testing these tables", 35],
            [u"comment", u"#Comment on line 29", 36],
            [u"step", u"Then ", u"I am happy", 37],
            [u"scenario", u"Scenario", u"Hammerzeit", u"", 39],
            [u"step", u"Given ", u"All work and no play", 40],
            [u"doc_string", u'', u"Makes Homer something something\nAnd something else", 41 ],
            [u"step", u"Then ", u"crazy", 45],
            [u"eof"],
        ])

    def test_find_things_in_right_order_for_crlf_feature(self):
        self.scan_file("dos_line_endings.feature")
        self.check([
            [u"comment", u"#Comment on line 1", 1],
            [u"comment", u"#Comment on line 2", 2],
            [u"tag", u"@tag1", 3],
            [u"tag", u"@tag2", 3],
            [u"feature", u"Feature", u"Feature Text", u"In order to test multiline forms\r\nAs a ragel writer\r\nI need to check for complex combinations", 4],
            [u"comment", u"#Comment on line 9", 9],
            [u"comment", u"#Comment on line 11", 11],
            [u"background", u"Background", u"", u"", 13],
            [u"step", u"Given ", u"this is a background step", 14],
            [u"step", u"And ", u"this is another one", 15],
            [u"tag", u"@tag3", 17],
            [u"tag", u"@tag4", 17],
            [u"scenario", u"Scenario", u"Reading a Scenario", u"", 18],
            [u"step", u"Given ", u"there is a step", 19],
            [u"step", u"But ", u"not another step", 20],
            [u"tag", u"@tag3", 22],
            [u"scenario", u"Scenario", u"Reading a second scenario", u"With two lines of text", 23],
            [u"comment", u"#Comment on line 24", 25],
            [u"step", u"Given ", u"a third step with a table", 26],
            [u"row", [u"a", u"b"], 27],
            [u"row", [u"c", u"d"], 28],
            [u"row", [u"e", u"f"], 29],
            [u"step", u"And ", u"I am still testing things", 30],
            [u"row", [u"g", u"h"], 31],
            [u"row", [u"e", u"r"], 32],
            [u"row", [u"k", u"i"], 33],
            [u"row", [u'n', u''], 34],
            [u"step", u"And ", u"I am done testing these tables", 35],
            [u"comment", u"#Comment on line 29", 36],
            [u"step", u"Then ", u"I am happy", 37],
            [u"scenario", u"Scenario", u"Hammerzeit", u"", 39],
            [u"step", u"Given ", u"All work and no play", 40],
            [u"doc_string", u'', u"Makes Homer something something\r\nAnd something else", 41],
            [u"step", u"Then ", u"crazy", 45],
            [u"eof"],
        ])
    
    @tools.raises(LexingError)
    def test_should_raise_error_if_unparsable_token_is_found_1(self):
        self.scan(u"Some text\nFeature: Hi")
    
    @tools.raises(LexingError)
    def test_should_raise_error_if_unparsable_token_is_found_2(self):
        self.scan(u"Feature: Hi\nBackground:\nGiven something\nScenario A scenario")
        
    @tools.raises(LexingError)
    def test_should_raise_error_if_unparsable_token_is_found_3(self):
        self.scan(u"Scenario: My scenario\nGiven foo\nAand bar\nScenario: another one\nGiven blah")
    
    def _test_should_include_the_line_number_and_context_of_the_error(self):
        assert False
    
    def test_feature_keyword_should_terminate_narratives_for_multiline_capable_tokens(self):
        self.scan(u"Feature:\nBackground:\nFeature:\nScenario Outline:\nFeature:\nScenario:\nFeature:\nExamples:\nFeature:\n")
        self.check([
            [u"feature", u"Feature", u"", u"", 1],
            [u"background", u"Background", u"", u"", 2],
            [u"feature", u"Feature", u"", u"", 3],
            [u"scenario_outline", u"Scenario Outline", u"", u"", 4],
            [u"feature", u"Feature", u"", u"", 5],
            [u"scenario", u"Scenario", u"", u"", 6],
            [u"feature", u"Feature", u"", u"", 7],
            [u"examples", u"Examples", u"","",  8],
            [u"feature", u"Feature", u"", u"", 9],
            [u"eof"],
        ])
