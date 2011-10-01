# -*- coding: utf8 -*-

import os.path
import unittest

from nose import tools

from gherkin.i18n import I18n
from gherkin.lexer.i18n_lexer import I18nLexer
from gherkin.sexp_recorder import SexpRecorder

# XXX: CONTAINS UNPORTED TESTS

class TestI18n(unittest.TestCase):
    def setUp(self):
        self.listener = SexpRecorder()

    def scan_file(self, lexer, filename):
        here = os.path.dirname(__file__)
        fixtures = os.path.join(here, '..', '..', 'spec', 'gherkin', 'fixtures')
        path = os.path.join(fixtures, filename)
        return lexer.scan(open(path, 'r').read())

    def test_recognize_keywords_in_the_language_of_the_lexer(self):
        lexer = I18nLexer(self.listener)
        self.scan_file(lexer, 'i18n_no.feature')
        tools.eq_(self.listener.sexps, [
            [u'comment', u"#language:no", 1],
            [u'feature', u"Egenskap", u"i18n support", u"", 2],
            [u'scenario', u"Scenario", u"Parsing many languages", u"", 4],
            [u'step', u"Gitt ", u"Gherkin supports many languages", 5],
            [u'step', u"Når ",  u"Norwegian keywords are parsed", 6],
            [u'step', u"Så ", u"they should be recognized", 7],
            [u'eof']
        ])

    def test_parse_languages_without_a_space_after_keywords(self):
        lexer = I18nLexer(self.listener)
        self.scan_file(lexer, 'i18n_zh-CN.feature')
        tools.eq_(self.listener.sexps, [
          [u"comment", u"#language:zh-CN", 1],
          [u"feature", u"功能", u"加法", u"", 2],
          [u"scenario", u"场景", u"两个数相加", u"", 4],
          [u"step", u"假如", u"我已经在计算器里输入6", 5],
          [u"step", u"而且", u"我已经在计算器里输入7", 6],
          [u"step", u"当", u"我按相加按钮", 7],
          [u"step", u"那么", u"我应该在屏幕上看到的结果是13", 8],
          [u"eof"]
        ])

    def test_parse_langauges_with_spaces_after_some_keywords_but_not_others(self):
        lexer = I18nLexer(self.listener)
        self.scan_file(lexer, 'i18n_fr.feature')
        tools.eq_(self.listener.sexps, [
          [u"comment", u"#language:fr", 1],
          [u"feature", u"Fonctionnalité", u"Addition", u"", 2],
          [u"scenario_outline", u"Plan du scénario", u"Addition de produits dérivés", u"", 3],
          [u"step", u"Soit ", u"une calculatrice", 4],
          [u"step", u"Etant donné ", u"qu'on tape <a>", 5],
          [u"step", u"Et ", u"qu'on tape <b>", 6],
          [u"step", u"Lorsqu'", u"on tape additionner", 7],
          [u"step", u"Alors ", u"le résultat doit être <somme>", 8],
          [u"examples", u"Exemples", u"", u"", 10],
          [u"row", [u'a', u'b', u'somme'], 11],
          [u"row", [u'2', u'2', u'4'], 12],
          [u"row", [u'2', u'3', u'5'], 13],
          [u"eof"]
        ])

    def test_have_code_keywords_without_punctuation(self):
        code_keywords = (u'Avast', u'Akkor', u'Etantdonné', u'Lorsque', u'假設')
        for code_keyword in code_keywords:
            assert code_keyword in I18n.all_code_keywords()

    def test_reject_bullet_stars(self):
        assert '*' not in I18n.all_code_keywords()

    def test_report_keyword_regexp(self):
        expected_substring = '|Quando |Quand |Quan |Pryd |Pokud |'
        assert expected_substring in I18n.keyword_regexp('step')

    def test_print_available_languages(self):
        assert u"\n" + I18n.language_table() == u"""
      | ar        | Arabic              | العربية           |
      | bg        | Bulgarian           | български         |
      | ca        | Catalan             | català            |
      | cs        | Czech               | Česky             |
      | cy-GB     | Welsh               | Cymraeg           |
      | da        | Danish              | dansk             |
      | de        | German              | Deutsch           |
      | en        | English             | English           |
      | en-Scouse | Scouse              | Scouse            |
      | en-au     | Australian          | Australian        |
      | en-lol    | LOLCAT              | LOLCAT            |
      | en-pirate | Pirate              | Pirate            |
      | en-tx     | Texan               | Texan             |
      | eo        | Esperanto           | Esperanto         |
      | es        | Spanish             | español           |
      | et        | Estonian            | eesti keel        |
      | fi        | Finnish             | suomi             |
      | fr        | French              | français          |
      | he        | Hebrew              | עברית             |
      | hr        | Croatian            | hrvatski          |
      | hu        | Hungarian           | magyar            |
      | id        | Indonesian          | Bahasa Indonesia  |
      | is        | Icelandic           | Íslenska          |
      | it        | Italian             | italiano          |
      | ja        | Japanese            | 日本語               |
      | ko        | Korean              | 한국어               |
      | lt        | Lithuanian          | lietuvių kalba    |
      | lu        | Luxemburgish        | Lëtzebuergesch    |
      | lv        | Latvian             | latviešu          |
      | nl        | Dutch               | Nederlands        |
      | no        | Norwegian           | norsk             |
      | pl        | Polish              | polski            |
      | pt        | Portuguese          | português         |
      | ro        | Romanian            | română            |
      | ru        | Russian             | русский           |
      | sk        | Slovak              | Slovensky         |
      | sr-Cyrl   | Serbian             | Српски            |
      | sr-Latn   | Serbian (Latin)     | Srpski (Latinica) |
      | sv        | Swedish             | Svenska           |
      | tr        | Turkish             | Türkçe            |
      | uk        | Ukrainian           | Українська        |
      | uz        | Uzbek               | Узбекча           |
      | vi        | Vietnamese          | Tiếng Việt        |
      | zh-CN     | Chinese simplified  | 简体中文              |
      | zh-TW     | Chinese traditional | 繁體中文              |
"""

    def test_print_keyword_for_a_given_language(self):
        assert u"\n" + I18n.get('fr').keyword_table() == u"""
      | feature          | "Fonctionnalité"                       |
      | background       | "Contexte"                             |
      | scenario         | "Scénario"                             |
      | scenario_outline | "Plan du scénario", "Plan du Scénario" |
      | examples         | "Exemples"                             |
      | given            | "* ", "Soit ", "Etant donné "          |
      | when             | "* ", "Quand ", "Lorsque ", "Lorsqu'"  |
      | then             | "* ", "Alors "                         |
      | and              | "* ", "Et "                            |
      | but              | "* ", "Mais "                          |
      | given (code)     | "Soit", "Etantdonné"                   |
      | when (code)      | "Quand", "Lorsque", "Lorsqu"           |
      | then (code)      | "Alors"                                |
      | and (code)       | "Et"                                   |
      | but (code)       | "Mais"                                 |
"""

if __name__ == '__main__':
    unittest.main()
