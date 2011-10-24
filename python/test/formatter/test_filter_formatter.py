import os.path
import re
import StringIO
import unittest

from nose import tools

from gherkin.parser import Parser
from gherkin.formatter.filter_formatter import FilterFormatter
from gherkin.formatter.pretty_formatter import PrettyFormatter

class FilterFormatterTestCase(unittest.TestCase):
    def setUp(self):
        self.file = 'complex_for_filtering.feature'
    
    def verify_filter(self, filters, *line_ranges):
        io = StringIO.StringIO()
        pretty_formatter = PrettyFormatter(io, True, False)
        filter_formatter = FilterFormatter(pretty_formatter, filters)
        parser = Parser(filter_formatter)
        
        path = os.path.dirname(__file__)
        path = os.path.join(path, '..', '..', '..', 'spec', 'gherkin')
        path = os.path.join(path, 'fixtures', self.file)
        source = open(path).read() + "# __EOF__"
        parser.parse(source, path, 0)
        
        source_lines = source.split('\n')
        expected = []
        for line_range in line_ranges:
            expected.extend(source_lines[line_range[0] - 1:line_range[1]])
        expected = '\n'.join(expected)
        expected = expected.replace('# __EOF__', '')
        tools.eq_(io.getvalue(), expected)

class TestFilterFormatterTags(FilterFormatterTestCase):
    def test_filter_on_feature_tag(self):
        self.verify_filter(['@tag1'], (1, 61))
    
    def test_filter_on_scenario_tag(self):
        self.verify_filter(['@tag4'], (1, 19))
    
    def test_filter_on_another_scenario_tag(self):
        self.verify_filter(['@tag3'], (1, 37))
    
    def test_filter_on_scenario_outline_tag(self):
        self.verify_filter(['@more'], (1, 14), (46, 61))
    
    def test_filter_on_first_examples_tag(self):
        self.verify_filter(['@neat'], (1, 14), (46, 55))
    
    def test_filter_on_second_examples_tag(self):
        self.verify_filter(['@hamster'], (1, 14), (46, 49), (56, 61))
    
    def test_not_replay_examples_from_ignored_scenario_outline(self):
        self.file = 'scenario_outline_with_tags.feature'
        self.verify_filter(['~@wip'], (1, 2), (12, 14))
    
    def test_not_choke_on_exmples_with_only_header(self):
        self.file = 'examples_with_only_header.feature'
        self.verify_filter(['@failing'], (1, 7), (12, 15))

class TestFilterFormatterNames(FilterFormatterTestCase):
    def test_filter_on_scenario_name(self):
        self.verify_filter([re.compile('Reading a Scenario')], (1, 19))
    
    def test_filter_on_scenario_outline_name(self):
        self.verify_filter([re.compile('More')], (1, 14), (46, 61))
    
    def test_filter_on_first_examples_name(self):
        self.verify_filter([re.compile('Neato')], (1, 14), (46, 55))
    
    def test_filter_on_second_examples_name(self):
        self.verify_filter([re.compile('Rodents')], (1, 14), (46, 49), (56, 61))
    
    def test_filter_on_various_names(self):
        self.file = 'hantu_pisang.feature'
        self.verify_filter([re.compile('Pisang')], (1, 8), (19, 32))
    
    def test_filter_on_background_name(self):
        self.file = 'hantu_pisang.feature'
        self.verify_filter([re.compile('The background')], (1, 5))
        
    def test_should_not_choke_on_examples_with_only_header(self):
        self.file = 'examples_with_only_header.feature'
        self.verify_filter([re.compile('B')], (1, 7), (12, 15))

class TestFilterFormatterLines1(FilterFormatterTestCase):
    # on the same line as feature element keyword
    
    def test_filter_on_scenario_without_line(self):
        self.file = 'scenario_without_steps.feature'
        self.verify_filter([3], (1, 4))
    
    def test_filter_on_scenario_line(self):
        self.verify_filter([16], (1, 19))
    
    def test_filter_on_scenario_outline_line(self):
        self.verify_filter([47], (1, 14), (46, 61))
    
    def test_filter_on_first_examples_line(self):
        self.verify_filter([51], (1, 14), (46, 55))
    
    def test_filter_on_second_examples_line(self):
        self.verify_filter([57], (1, 14), (46, 49), (56, 61))
    
    def test_should_not_choke_on_examples_with_only_header(self):
        self.file = 'examples_with_only_header.feature'
        self.verify_filter([13], (1, 7), (12, 15))
        self.verify_filter([14], (1, 7), (12, 15))

class TestFilterFormatterLines2(FilterFormatterTestCase):
    # on the same line as step keyword
    
    def test_filter_on_step_line(self):
        self.verify_filter([17], (1, 19))
    
    def test_filter_on_scenario_outline_line(self):
        self.verify_filter([48], (1, 14), (46, 61))
    
class TestFilterFormatterLines3(FilterFormatterTestCase):
    # on examples header line
    
    def test_filter_on_first_table(self):
        self.verify_filter([52], (1, 14), (46, 55))
    
    def test_filter_on_second_table(self):
        self.verify_filter([58], (1, 14), (46, 49), (56, 61))

class TestFilterFormatterLines4(FilterFormatterTestCase):
    # on examples example line
    
    def test_filter_on_first_table(self):
        self.verify_filter([53], (1, 14), (46, 53), (55, 55))

class TestFilterFormatterLines5(FilterFormatterTestCase):
    # on tag line
    
    def test_filter_on_first_tag(self):
        self.verify_filter([15], (1, 19))
    
class TestFilterFormatterLines6(FilterFormatterTestCase):
    # multiline argument
    
    def test_filter_on_table_line(self):
        self.verify_filter([36], (1, 14), (20, 37))
    
    def test_filter_on_first_pystring_quote(self):
        self.verify_filter([41], (1, 14), (38, 45))
    
    def test_filter_on_last_pystring_quote(self):
        self.verify_filter([44], (1, 14), (38, 45))
