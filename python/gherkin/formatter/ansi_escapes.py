import os

colors = {
    'black':    "\x1b[30m",
    'red':      "\x1b[31m",
    'green':    "\x1b[32m",
    'yellow':   "\x1b[33m",
    'blue':     "\x1b[34m",
    'magenta':  "\x1b[35m",
    'cyan':     "\x1b[36m",
    'white':    "\x1b[37m",
    'grey':     "\x1b[90m",
    'bold':     "\x1b[1m",
}

aliases = {
    'undefined':    'yellow',
    'pending':      'yellow',
    'executing':    'grey',
    'failed':       'red',
    'passed':       'green',
    'outline':      'cyan',
    'skipped':      'cyan',
    'comments':     'grey',
    'tag':          'cyan',
}

if 'GHERKIN_COLORS' in os.environ:
    colors = [p.split('=') for p in os.environ['GHERKIN_COLORS'].split(':')]
    aliases.update(dict(colors))

for alias in aliases:
    locals()[alias] = ''.join([colors[c] for c in aliases[alias].split(',')])
    arg_alias = alias + '_arg'
    arg_seq = aliases.get(arg_alias, aliases[alias] + ',bold')
    locals()[arg_alias] = ''.join([colors[c] for c in arg_seq.split(',')])

def reset():
    return "\x1b[0m"

def up(n):
    return "\x1b[#%dA" % n
