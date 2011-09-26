import unittest

from gherkin.formatter.ansi_escapes import escapes

class TestANSIEscapes(unittest.TestCase):
    def test_failed_should_be_red(self):
        assert escapes['failed'] == '\x1b[31m'

    def test_failed_arg_should_be_red_bold(self):
        assert escapes['failed_arg'] == '\x1b[31m\x1b[1m'
