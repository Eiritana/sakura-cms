"""Sakura functions for parsing. Loads Python modules from the function
directory to utilize them in Sakura %%func function_name%% substitutions,
for parsing a document.

"""

import common as lib
from glob import glob
import os


def load_functions(public):
    """Returns a dictionary of "functions" (functions)
    and their arguments.
    
    Load functions to evaluate arguments/values pre-defined in "public"
    (dictionary).

    Args:
      public (dict): Keyword arguments any function may
        select from by key.

    Returns:
        dict: key is the func name/module name, and the values are
          a three-element tuple:
          (function, argument [tuple], replace_all [bool])

    """

    settings = lib.ini('settings')
    package = settings['directories']['function']
    functions = {}

    for file_name in glob(package + '/*.py'):
        module_name, __ = os.path.splitext(os.path.basename(file_name))

        if module_name == "__init__":
            continue

        # import the module and the keys/arguments
        module_import = "%s.%s" % (package, module_name)
        config_variables = ('SAKURA_ARGS', 'REPLACE_ALL')
        args = __import__(module_import, fromlist=config_variables)
        replace_all = args.REPLACE_ALL
        args = args.SAKURA_ARGS

        # load pre-defined arguments via keys/arguments
        args = [public[arg] for arg in args]
        func = __import__(module_import, fromlist=[module_name])
        func = getattr(func, module_name)
        functions[module_name] = (func, args, replace_all)

    return functions

