import imp
import os.path

lexer_cache = {}

def get_lexer(iso_code, listener):
    if iso_code in lexer_cache:
        return lexer_cache[iso_code](listener)

    path = os.path.dirname(__file__)
    name = 'lexer_' + iso_code
    modfile, pathname, description = imp.find_module(name, [path])
    if modfile is None:
        return None
    module = None
    try:
        module = imp.load_module(name, modfile, pathname, description)
    finally:
        modfile.close()
    if module is None:
        return None

    lexer = module.Lexer(listener)
    lexer_cache[iso_code] = module.Lexer
    return lexer
