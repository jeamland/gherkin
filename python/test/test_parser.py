# -*- coding: utf8 -*-

import inspect
import unittest

from mock import Mock
from nose import tools

from gherkin.formatter.pretty_formatter import PrettyFormatter
from gherkin.parser import Parser, ParseError

class TestParser(unittest.TestCase):
    def test_should_raise_when_feature_does_not_parse(self):
        p = Parser(Mock(PrettyFormatter))
        with tools.assert_raises(ParseError):
            p.parse(u"Feature: f\nFeature: f", __file__,
                    inspect.currentframe().f_back.f_lineno - 1)
