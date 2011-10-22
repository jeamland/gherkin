import os.path
import types

from gherkin.i18n import I18n
from gherkin.lexer.i18n_lexer import I18nLexer
from gherkin.listener import FormatterListener
from gherkin.formatter.pretty_formatter import PrettyFormatter

class ParseError(Exception):
    pass

class Parser(object):
    def __init__(self, formatter, raise_on_error=True, machine_name='root'):
        self.formatter = formatter
        self.raise_on_error = raise_on_error
        self.machine_name = machine_name

        self.line_offset = None
        self.i18n_language = None
        self.feature_uri = None

        self.listener = FormatterListener(self.formatter)
        self.machines = []
        self.push_machine(machine_name)
        self.lexer = I18nLexer(self)

    def parse(self, gherkin, feature_uri, line_offset):
        self.feature_uri = feature_uri
        self.formatter.uri(feature_uri)
        self.line_offset = line_offset
        self.lexer.scan(gherkin)

    def __getattr__(self, name):
        attr = getattr(self.listener, name)
        if type(attr) is not types.MethodType:
            raise AttributeError
        def wrapper(*args):
            if args[0] is self:
                args = args[1:]
            if name == u'eof':
                self.event(name, None)
            else:
                self.event(name, args[-1])
            attr(*args)
            if name == u'eof':
                self.pop_machine()
                self.push_machine(self.machine_name)

        setattr(self, name, wrapper)
        return wrapper.__get__(self, self.__class__)

    def event(self, event, line):
        if line:
            line = self.line_offset + line
        else:
            line = None

        self.machine.event(event, line)
        if not self.machine.error:
            return

        state = self.machine.state
        legal_events = self.machine.expected

        if self.raise_on_error:
            raise ParseError(state, event, legal_events, self.feature_uri, line)
        else:
            self.listener.syntax_error(state, event, legal_events,
                                       self.feature_uri, line)

    def push_machine(self, name):
        self.machines.append(Machine(self, name))

    def pop_machine(self):
        self.machines.pop()

    @property
    def machine(self):
        return self.machines[-1]

    @property
    def expected(self):
        return self.machine.expected

    def force_state(self, state):
        self.machine.state = state

class StateMachineReader(object):
    def __init__(self):
        self.rows = []

    def uri(self, uri):
        pass

    def row(self, row, line_number):
        self.rows.append(row)

    def eof(self):
        pass

class Machine(object):
    transition_maps = {}

    def __init__(self, parser, name):
        self.parser = parser
        self.name = name

        self.transition_map = self._transition_map(name)
        self.state = name

        self.legal_events = None
        self.error = False

    def event(self, event, line):
        states = self.transition_map[self.state]

        new_state = states[event]

        if new_state == 'E':
            self.error = True
            return

        if new_state.startswith('push('):
            self.parser.push_machine(new_state[5:-1])
            self.parser.event(event, line)
        elif new_state == 'pop()':
            self.parser.pop_machine()
            self.parser.event(event, line)
        else:
            if new_state is None:
                raise ParseError()
            self.state = new_state

    @property
    def expected(self):
        transition_map = self.transition_map[self.state]
        events = [s for s in transition_map if transition_map[s] != 'E']
        events.sort()
        events.remove(u'eof')
        return events

    def _transition_map(self, name):
        transition_map = self.transition_maps.get(name, None)
        if transition_map is not None:
            return transition_map

        transition_map = self.build_transition_map(name)
        self.transition_maps[name] = transition_map
        return transition_map

    def build_transition_map(self, name):
        table = self.transition_table(name)
        events = table.pop(0)[1:]
        transition_map = {}
        for row in table:
            transition_map[row[0]] = dict(zip(events, row[1:]))
        return transition_map

    def transition_table(self, name):
        state_machine_reader = StateMachineReader()
        lexer = I18n('en').lexer(state_machine_reader)
        machine = os.path.dirname(__file__)
        machine = os.path.join(machine, 'parser_data', name + '.txt')
        lexer.scan(open(machine).read())
        return state_machine_reader.rows
