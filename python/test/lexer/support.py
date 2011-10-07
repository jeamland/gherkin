import os.path
import unittest

from nose import tools

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
