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

        # import the module...
        module_import = "%s.%s" % (package, module_name)

        # attempt to read and utilize the function's CONFIG settings
        function_config = __import__(module_import, fromlist=["CONFIG"])
        function_config = function_config.CONFIG
        replaces = function_config['replaces']  # what text ((calls)) this function

        # load pre-defined 
        args = [public[arg] for arg in function_config['args']]
        calls = function_config['calls']
        func = __import__(module_import, fromlist=[calls])
        func = getattr(func, calls)
        functions[replaces] = (func, args)

    return functions

