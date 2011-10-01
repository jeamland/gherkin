from gherkin.formatter import model

def handle_event(event):
    def handler(self, *args):
        self.sexps.append([event] + self.sexpify(args))
    return handler

class SexpRecorder(object):
    def __init__(self):
        self.sexps = []

    comment = handle_event(u'comment')
    tag = handle_event(u'tag')
    feature = handle_event(u'feature')
    background = handle_event(u'background')
    scenario = handle_event(u'scenario')
    scenario_outline = handle_event(u'scenario_outline')
    examples = handle_event(u'examples')
    step = handle_event(u'step')
    doc_string = handle_event(u'doc_string')
    row = handle_event(u'row')
    eof = handle_event(u'eof')
    uri = handle_event(u'uri')
    syntax_error = handle_event(u'syntax_error')

    def errors(self):
        return [sexp for sexp in self.sexps if sexp[0] == u'syntax_error']

    def line(self, number):
        for sexp in self.sexps:
            if sexp.last == number:
                return sexp
        return None

    def sexpify(self, obj):
        if type(obj) in (list, tuple):
            return [self.sexpify(event) for event in obj]
        elif type(obj) is model.Row:
            return {
                u'cells': self.sexpify(obj.cells),
                u'comments': self.sexpify(obj.comments),
                u'line': obj.line
            }
        elif type(obj) is model.Comment:
            return obj.value
        elif type(obj) is model.Tag:
            return obj.name
        return obj
