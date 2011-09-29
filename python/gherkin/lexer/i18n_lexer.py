import re

from gherkin.i18n import I18n

newline = re.compile(r'\r|\n|(?:\r\n)|(?:\n\r)')
comment_or_empty_line = re.compile(r'^\s*#|^\s*$')
language_pattern = re.compile(r'^\s*#\s*language\s*:\s*([a-zA-Z\-]+)')

def lazy_split_lines(data):
    current = 0
    while True:
        last = current
        current = data.find('\n', current + 1)
        if current == -1:
            break
        yield data[last:current]

class I18nLexer(object):
    def __init__(self, listener):
        self.listener = listener
        self.i18n_language = None

    def scan(self, source):
        self.create_delegate(source).scan(source)

    def create_delegate(self, source):
        self.i18n_language = self.lang(source)
        return self.i18n_language.lexer(self.listener)

    def lang(self, source):
        key = 'en'
        for line in lazy_split_lines(source):
            if not comment_or_empty_line.match(line):
                break
            match = language_pattern.match(line)
            if match:
                key = match.groups(1)[0]
        return I18n.get(key)
