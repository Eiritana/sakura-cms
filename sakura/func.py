"""Sakura functions for parsing. Loads Python modules from the function
directory to utilize them in Sakura %%func function_name%% substitutions,
for parsing a document.

"""

import common as lib
from glob import glob
import os


def load_functions(public):
    """Returns a dictionary of "functions" (functions) and their arguments.
    
    Load functions to evaluate arguments/values pre-defined in "public"
    (dictionary).

    public (dict) -- Keyword arguments any function may select from by key.

    """

    package = lib.SETTINGS['directories']['function']
    functions = {}

    for file_name in glob(package + '/*.py'):
        module_name, __ = os.path.splitext(os.path.basename(file_name))

        if module_name == "__init__":
            continue

        # import the module and the keys/arguments
        module_import = "%s.%s" % (package, module_name)
        args = __import__(module_import, fromlist=["SAKURA_ARGS"])
        args = args.SAKURA_ARGS

        # load pre-defined arguments via keys/arguments
        args = [public[arg] for arg in args]
        func = __import__(module_import, fromlist=[module_name])
        func = getattr(func, module_name)
        functions[module_name] = (func, args)

    return functions

