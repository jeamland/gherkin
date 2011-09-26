# -*- coding: utf8 -*-

import cStringIO
import unittest

from gherkin.formatter import argument, model
from gherkin.formatter.ansi_escapes import escapes, up
from gherkin.formatter.pretty_formatter import PrettyFormatter

# XXX: CONTAINS UNPORTED TESTS


class TestPrettyFormatter(unittest.TestCase):
    def setUp(self):
        self.stream = cStringIO.StringIO()
        self.f = PrettyFormatter(self.stream, False, True)

    def assert_stream(self, string):
        have = self.stream.getvalue().decode('utf8')
        print repr(have)
        print repr(string)
        assert have == string

    def test_print_comments_when_scenario_is_longer(self):
        self.f.uri('features/foo.feature')
        self.f.feature(model.Feature([], [], 'Feature', 'Hello', 'World', 1))

        self.f.scenario(model.Scenario([], [], 'Scenario', 'The scenario',
                                       '', 4))
        self.f.step(model.Step([], 'Given ', 'some stuff', 5))
        self.f.step(model.Step([], 'When ', 'foo', 6))

        self.f.match(model.Match([], 'features/step_definitions/bar.py:56'))
        self.f.result(model.Result('passed', 22, None))

        self.f.match(model.Match([], 'features/step_definitions/bar.py:96'))
        self.f.result(model.Result('passed', 33, None))

        self.assert_stream(u"""Feature: Hello
  World

  Scenario: The scenario {comments}# features/foo.feature:4{reset}
    {executing}Given {reset}{executing}some stuff{reset}     {comments}# features/step_definitions/bar.py:56{reset}
{up}    {passed}Given {reset}{passed}some stuff{reset}     {comments}# features/step_definitions/bar.py:56{reset}
    {executing}When {reset}{executing}foo{reset}             {comments}# features/step_definitions/bar.py:96{reset}
{up}    {passed}When {reset}{passed}foo{reset}             {comments}# features/step_definitions/bar.py:96{reset}
        """.rstrip(' ').format(**escapes))

    def test_print_comments_when_step_is_longer(self):
        self.f.uri('features/foo.feature')
        self.f.feature(model.Feature([], [], 'Feature', 'Hello', 'World', 1))
        step = model.Step([], 'Given ', 'some stuff that is longer', 5)
        match = model.Match([], 'features/step_definitions/bar.py:56')
        result = model.Result('passed', 0, None)

        self.f.scenario(model.Scenario([], [], 'Scenario', 'The scenario',
                                       '', 4))
        self.f.step(step)
        self.f.match(match)
        self.f.result(result)

        self.assert_stream(u"""Feature: Hello
  World

  Scenario: The scenario            {comments}# features/foo.feature:4{reset}
    {executing}Given {reset}{executing}some stuff that is longer{reset} {comments}# features/step_definitions/bar.py:56{reset}
{up}    {passed}Given {reset}{passed}some stuff that is longer{reset} {comments}# features/step_definitions/bar.py:56{reset}
        """.rstrip(' ').format(**escapes))

    def test_highlight_arguments_for_regular_steps(self):
        self.f.uri('foo.feature')
        self.f.scenario(model.Scenario([], [], 'Scenario', 'Lots of cukes',
                                       '', 3))
        self.f.step(model.Step([], 'Given ', 'I have 999 cukes in my belly', 3))
        self.f.match(model.Match([argument.Argument(7, '999')], None))
        self.f.result(model.Result('passed', 6, None))

        self.assert_stream(u"""
  Scenario: Lots of cukes              {comments}# foo.feature:3{reset}
    {executing}Given {reset}{executing}I have {reset}{executing_arg}999{reset}{executing} cukes in my belly{reset}
{up}    {passed}Given {reset}{passed}I have {reset}{passed_arg}999{reset}{passed} cukes in my belly{reset}
        """.rstrip(' ').format(**escapes))

    '''
          it "should prettify scenario" do
            assert_pretty(%{Feature: Feature Description
      Some preamble

      Scenario: Scenario Description
        description has multiple lines

        Given there is a step
          """
          with
            pystrings
          """
        And there is another step
          | æ   | \\|o |
          | \\|a | ø\\\\ |
        Then we will see steps
    })
          end
    '''

    '''
          it "should prettify scenario outline with table" do
            assert_pretty(%{# A feature comment
    @foo
    Feature: Feature Description
      Some preamble
      on several
      lines

      # A Scenario Outline comment
      @bar
      Scenario Outline: Scenario Ouline Description
        Given there is a
          """
          string with <foo>
          """
        And a table with
          | <bar> |
          | <baz> |

        @zap @boing
        Examples: Examples Description
          | foo    | bar  | baz         |
          | Banana | I    | am hungry   |
          | Beer   | You  | are thirsty |
          | Bed    | They | are tired   |
    })
          end
    '''

    '''
    it "should preserve tabs" do
      assert_pretty(IO.read(File.dirname(__FILE__) + '/tabs.feature'), IO.read(File.dirname(__FILE__) + '/spaces.feature'))
    end
    '''

    def test_escape_backslashes_and_pipes(self):
        self.f.table([model.Row([], ['|', '\\'], 1)])
        self.assert_stream(u'      | \\| | \\\\ |\n')
