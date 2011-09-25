# -*- coding: utf8 -*-

import cStringIO
import codecs
import unittest

from gherkin.formatter.argument import Argument
from gherkin.formatter.step_printer import StepPrinter

utf8decode = codecs.getdecoder('utf8')

class ParenthesisFormat(object):
    def text(self, text):
        if type(text) is str:
            text = utf8decode(text)[0]
        return u"(" + text + u")"

class BracketFormat(object):
    def text(self, text):
        if type(text) is str:
            text = utf8decode(text)[0]
        return u"[" + text + u"]"

class TestStepPrinter(unittest.TestCase):
    def setUp(self):
        utf8writer = codecs.getwriter('utf8')
        self.stringio = cStringIO.StringIO()
        self.stream = utf8writer(self.stringio)
        self.printer = StepPrinter()
        self.pf = ParenthesisFormat()
        self.bf = BracketFormat()

    def write_step(self, step_name, arguments):
        self.printer.write_step(self.stream, self.pf, self.bf, step_name,
                                arguments)

    def test_replace_0_args(self):
        self.write_step("I have 10 cukes", [])
        assert self.stream.getvalue() == "(I have 10 cukes)"

    def test_replace_1_arg(self):
        self.write_step("I have 10 cukes", [Argument(7, '10')])
        assert self.stream.getvalue() == "(I have )[10]( cukes)"

    def test_replace_1_unicode_arg(self):
        self.write_step(u"I hæve øæ cåkes", [Argument(7, u'øæ')])
        assert utf8decode(self.stream.getvalue())[0] == u"(I hæve )[øæ]( cåkes)"

    def test_replace_2_args(self):
        self.write_step("I have 10 yellow cukes in my belly",
                        [Argument(7, '10'), Argument(17, 'cukes')])
        assert self.stream.getvalue() == \
            "(I have )[10]( yellow )[cukes]( in my belly)"

    def test_replace_2_unicode_args(self):
        self.write_step(u"Æslåk likes æøå",
                        [Argument(0, u'Æslåk'), Argument(12, u'æøå')])
        assert utf8decode(self.stream.getvalue())[0] == u"[Æslåk]( likes )[æøå]"
