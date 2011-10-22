import os.path
import unittest

from mock import Mock
from nose import tools

from gherkin.formatter.tag_count_formatter import TagCountFormatter
from gherkin.parser import Parser
from gherkin.sexp_recorder import SexpRecorder

class TestTagCountFormatter(unittest.TestCase):
    def test_should_count_tags(self):
        tag_counts = {}
        dummy = SexpRecorder()
        formatter = TagCountFormatter(dummy, tag_counts)
        parser = Parser(formatter)
        
        here = os.path.dirname(__file__)
        fixtures = os.path.join(here, '..', '..', '..', 'spec', 'gherkin')
        path = os.path.join(fixtures, 'fixtures', 'complex_with_tags.feature')
        gherkin = open(path).read()
        
        parser.parse(gherkin, 'f.feature', 0)
        
        tools.eq_(tag_counts, {
            u"@hamster": ["f.feature:58"],
            u"@tag1":    ["f.feature:18","f.feature:23","f.feature:39",
                          "f.feature:52","f.feature:58"],
            u"@tag2":    ["f.feature:18","f.feature:23","f.feature:39",
                          "f.feature:52","f.feature:58"],
            u"@tag3":    ["f.feature:18", "f.feature:23"],
            u"@tag4":    ["f.feature:18"],
            u"@neat":    ["f.feature:52"],
            u"@more":    ["f.feature:52", "f.feature:58"]
        })
        