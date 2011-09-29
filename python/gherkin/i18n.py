# -*- coding: utf8 -*-

import cStringIO
import os.path
import re

import yaml

from gherkin.formatter import model, pretty_formatter
from gherkin.lexer import ext as ext_lexer

here = os.path.dirname(__file__)
code_keyword_re = re.compile(r"[\s',!]")
whitespace_re = re.compile(r"\s")
underscore_re = re.compile(r"[\s-]")
real_keyword_re = re.compile(r"< $")

def construct_yaml_str(self, node):
    return self.construct_scalar(node)

yaml.Loader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)
yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)

def quote(value):
    return u'"' + value + u'"'

class I18n(object):
    FEATURE_ELEMENT_KEYS = [
        'feature',
        'background',
        'scenario',
        'scenario_outline',
        'examples',
    ]
    STEP_KEYWORD_KEYS = [
        'given',
        'when',
        'then',
        'and',
        'but',
    ]
    KEYWORD_KEYS = FEATURE_ELEMENT_KEYS + STEP_KEYWORD_KEYS
    LANGUAGES = yaml.load(open(os.path.join(here, 'i18n.yml')))

    languages = {}

    @classmethod
    def all(cls):
        codes = cls.LANGUAGES.keys()
        codes.sort()
        return [cls.get(iso_code) for iso_code in codes]

    @classmethod
    def get(cls, iso_code):
        i18n = cls.languages.get(iso_code, None)
        if i18n is not None:
            return i18n
        i18n = cls.languages[iso_code] = I18n(iso_code)
        return i18n

    @classmethod
    def keyword_regexp(cls, *keywords):
        unique_keywords = set()
        for i18n in cls.all():
            for keyword in keywords:
                if str(keyword) == 'step':
                    unique_keywords.update(i18n.step_keywords())
                else:
                    unique_keywords.update(i18n.keywords(keyword))

        unique_keywords = [unicode(k) for k in unique_keywords]
        unique_keywords.sort(reverse=True)
        return '|'.join(unique_keywords)

    @classmethod
    def all_code_keywords(cls):
        keywords = set(sum([i18n.code_keywords() for i18n in cls.all()], []))
        keywords = list(keywords)
        keywords.sort()
        return keywords

    @classmethod
    def code_keyword_for(cls, gherkin_keyword):
        return code_keyword_re.sub('', gherkin_keyword).strip()

    @classmethod
    def language_table(cls):
        stream = cStringIO.StringIO()
        formatter = pretty_formatter.PrettyFormatter(stream, False, False)
        table = []
        for i18n in cls.all():
            cells = [i18n.iso_code, i18n.keywords('name')[0],
                     i18n.keywords('native')[0]]
            table.append(model.Row([], cells, None))
        formatter.table(table)
        return stream.getvalue().decode('utf8')

    @classmethod
    def unicode_escape(cls, word, prefix="\\u"):
        chars = []
        for c in [ord(char) for char in word]:
            if c > 127 or c == 32:
                chars.append("%s%04x" % (prefix, c))
            else:
                chars.append(unichr(c))

        return ''.join(chars)

    def __init__(self, iso_code):
        self.iso_code = iso_code
        self._keywords = self.LANGUAGES.get(iso_code, None)
        if self._keywords is None:
            raise Exception("Language not supported: %r" % iso_code)
        self._keywords['grammar_name'] = \
            whitespace_re.sub('', self._keywords['name'])
        self.underscored_iso_code = \
            underscore_re.sub('_', self.iso_code).lower()

    def lexer(self, listener):
        return ext_lexer.get_lexer(self.underscored_iso_code, listener)

    def step_keywords(self):
        keywords = set()
        for iso_code in self.STEP_KEYWORD_KEYS:
            keywords.update(self.keywords(iso_code))
        return list(keywords)

    def code_keywords(self):
        keywords = [self.code_keyword_for(k) for k in self.step_keywords()]
        return [k for k in keywords if k != '*']

    def keywords(self, key):
        key = str(key)
        keywords = self._keywords[key].split('|')
        return [self.real_keyword(key, keyword) for keyword in keywords]

    def keyword_table(self):
        stream = cStringIO.StringIO()
        formatter = pretty_formatter.PrettyFormatter(stream, False, False)

        gherkin_keyword_table = []
        for key in self.KEYWORD_KEYS:
            cells = [key, ', '.join([quote(k) for k in self.keywords(key)])]
            gherkin_keyword_table.append(model.Row([], cells, None))

        code_keyword_table = []
        for key in self.STEP_KEYWORD_KEYS:
            code_keywords = []
            for keyword in self.keywords(key):
                if keyword == '* ':
                    continue
                code_keywords.append(self.code_keyword_for(keyword))
            code_keywords = ', '.join([quote(k) for k in code_keywords])
            cells = [key + ' (code)', code_keywords]
            code_keyword_table.append(model.Row([], cells, None))

        formatter.table(gherkin_keyword_table + code_keyword_table)
        return stream.getvalue().decode('utf8')

    def real_keyword(self, key, keyword):
        if key in self.STEP_KEYWORD_KEYS:
            return real_keyword_re.sub('', keyword + ' ')
        else:
            return keyword