import unittest

from gherkin.formatter import ansi_escapes

class TestANSIEscapes(unittest.TestCase):
    def test_failed_should_be_red(self):
        assert ansi_escapes.failed == '\x1b[31m'

    def test_failed_arg_should_be_red_bold(self):
        assert ansi_escapes.failed_arg == '\x1b[31m\x1b[1m'
