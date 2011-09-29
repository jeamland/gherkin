from gherkin.formatter import model

def handle_event(event):
    def handler(self, *args):
        self.sexps.append([event] + self.sexpify(args))
    return handler

class SexpRecorder(object):
    def __init__(self):
        self.sexps = []

    comment = handle_event('comment')
    tag = handle_event('tag')
    feature = handle_event('feature')
    background = handle_event('background')
    scenario = handle_event('scenario')
    scenario_outline = handle_event('scenario_outline')
    examples = handle_event('examples')
    step = handle_event('step')
    doc_string = handle_event('doc_string')
    row = handle_event('row')
    eof = handle_event('eof')
    uri = handle_event('uri')
    syntax_error = handle_event('syntax_error')

    def errors(self):
        return [sexp for sexp in self.sexps if sexp[0] == 'syntax_error']

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
                'cells': self.sexpify(obj.cells),
                'comments': self.sexpify(obj.comments),
                'line': obj.line
            }
        elif type(obj) is model.Comment:
            return obj.value
        elif type(obj) is model.Tag:
            return obj.name
        return obj
