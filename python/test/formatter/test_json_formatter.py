import json
from StringIO import StringIO
import unittest

from nose import tools

from gherkin.formatter.json_formatter import JSONFormatter
from gherkin.formatter import model

class TestJSONFormatter(unittest.TestCase):
    def test_renders_results(self):
        io = StringIO()
        f = JSONFormatter(io)
        
        f.uri(u"f.feature")
        f.feature(model.Feature([], [], u"Feature", u"f", u"", 1))
        f.scenario(model.Scenario([], [], u"Feature", u"f", u"", 2))
        f.step(model.Step([], u"Given ", u"g", 3))
        f.step(model.Step([], u"When ", u"w", 4))

        f.match(model.Match([], u"def.py:33"))
        f.result(model.Result(u"passed", 1, None))

        f.match(model.Match([], u"def.py:44"))
        f.result(model.Result(u"passed", 1, None))

        f.eof()
        
        expected = """
        {
          "keyword": "Feature",
          "name": "f",
          "line": 1,
          "description": "",
          "elements": [
            {
              "keyword": "Feature",
              "name": "f",
              "line": 2,
              "description": "",
              "type": "scenario",
              "steps": [
                {
                  "keyword": "Given ",
                  "name": "g",
                  "line": 3,
                  "match": {
                    "location": "def.py:33"
                  },
                  "result": {
                    "status": "passed",
                    "duration": 1
                  }
                },
                {
                  "keyword": "When ",
                  "name": "w",
                  "line": 4,
                  "match": {
                    "location": "def.py:44"
                  },
                  "result": {
                    "status": "passed",
                    "duration": 1
                  }
                }
              ]
            }
          ]
        }
        """
        
        tools.eq_(json.loads(expected), json.loads(io.getvalue()))
        