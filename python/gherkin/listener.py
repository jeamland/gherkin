from gherkin.formatter import model

class FormatterListener(object):
    def __init__(self, formatter):
        self.formatter = formatter
        self.comments = []
        self.tags = []
        self.rows = []
        self.examples_statement = None
        self.step_statement = None
        self.doc_string_statement = None

    def comment(self, value, line):
        self.comments.append(model.Comment(value, line))

    def tag(self, name, line):
        self.tags.append(model.Tag(name, line))

    def feature(self, keyword, name, description, line):
        feature = model.Feature(self.grab_comments(), self.grab_tags(),
                                keyword, name, description, line)
        self.formatter.feature(feature)

    def background(self, keyword, name, description, line):
        background = model.Background(self.grab_comments(), keyword, name,
                                      description, line)
        self.formatter.background(background)

    def scenario(self, keyword, name, description, line):
        self.replay_step_or_examples()
        scenario = model.Scenario(self.grab_comments(), self.grab_tags(),
                                  keyword, name, description, line)
        self.formatter.scenario(scenario)

    def scenario_outline(self, keyword, name, description, line):
        self.replay_step_or_examples()
        outline = model.ScenarioOutline(self.grab_comments(), self.grab_tags(),
                                        keyword, name, description, line)
        self.formatter.scenario_outline(outline)

    def examples(self, keyword, name, description, line):
        self.replay_step_or_examples()
        examples = model.Examples(self.grab_comments(), self.grab_tags(),
                                  keyword, name, description, line, None)
        self.examples_statement = examples

    def step(self, keyword, name, line):
        self.replay_step_or_examples()
        step = model.Step(self.grab_comments(), keyword, name, line)
        self.step_statement = step

    def row(self, cells, line):
        self.rows.append(model.Row(self.grab_comments(), cells, line))

    def doc_string(self, string, content_type, line):
        self.doc_string_statement = model.DocString(string, content_type, line)

    def eof(self):
        self.replay_step_or_examples()
        self.formatter.eof()

    def syntax_error(self, state, ev, legal_events, uri, line):
        self.formatter.syntax_error(state, ev, legal_events, uri, line)

    def grab_comments(self):
        comments = self.comments
        self.comments = []
        return comments

    def grab_tags(self):
        tags = self.tags
        self.tags = []
        return tags

    def replay_step_or_examples(self):
        if self.step_statement is not None:
            if self.doc_string_statement is not None:
                self.step_statement.doc_string = self.doc_string_statement
                self.doc_string_statement = None
            elif self.rows:
                self.step_statement.rows = self.rows
                self.rows = []
            self.formatter.step(self.step_statement)
            self.step_statement = None
        if self.examples_statement is not None:
            if self.rows:
                self.examples_statement.rows = self.rows
                self.rows = []
            self.formatter.examples(self.examples_statement)
            self.examples_statement = None
