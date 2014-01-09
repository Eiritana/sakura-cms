"""Sakura functions for parsing. Loads Python modules from the function
directory to utilize them in Sakura %%func function_name%% substitutions,
for parsing a document.

"""

import common as lib
from glob import glob
import os
import tag


def load(public):
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


def replace(document):
    """Replace Sakura functions ##func function-name args##

    Used for parsing the function list _cache, which specified functions to
    use on every document therein cache.

    Args:
      document (dict): the document being evaluated
        to find the functions. The dictionary contents being:

          * edit (str): the document to place the evaluation
              of the function in.
          * path (str):
          * contents (str):
          * no_return (bool): if True this function offers no
              return string.

    Returns:
      str: the version of the document contents, with the function
        tag calls evaluated and substituted.

    """

    contents = document['contents']
    document_path = document['path']
    edit_contents = document.get('edit_contents', None)
    new_contents = edit_contents or contents
    no_return = 'no_return' in document and document['no_return']

    # replace ((functions)) -- importantly last
    for element in tag.iter_tags('function', contents):
        new_contents = evaluate(
                                element,
                                new_contents,
                                document_path,
                                debug=edit_contents,
                                no_return=no_return,
                               )

    if no_return:
        return ''
    else:
        return new_contents


def evaluate(element, contents, document_path,
             debug=False, no_return=False):
    """Take a given Sakura ##func## element, and return the contents
    of said evaluation.

    I need to explain the rules of evaluation better herein.

    Args:
      element (dict): the dictionary generated from iter_tags().
      document (str): the document to edit with the element evaluation

    Returns:
        str: the document after evaluating/substituting a function tag.

    """

    user_defined_args = get_args(element['contents'])
    public = {  # room for elaboration on this...
              'document_path': document_path,
              'document': contents,
              'element_full': element['full'],
              'element_name': element['name'],
             }

    try:
        func_name = element['name']
        function, args, replace_all = load(public)[func_name]

    except KeyError:
        error_vars = (document_path, element['name'], element['full'])
        raise Exception('##func##    %s: %s is not loaded (%s)' % error_vars)

    # if we do have user defined arguments in the element,
    # then append them to the args!
    if user_defined_args:
        args.extend(user_defined_args)

    data = function(*args)

    if debug:
        return data

    if no_return:
        return ''

    if replace_all:
        return data.replace(element['full'], '')
    else:
        return contents.replace(element['full'], data)


def get_args(contents):
    """Return a list of arguments therein the contents of a Sakura element.

    If there are no arguments, returns None.

    Args:
      contents (str) -- example: "func config httpd basehref"

    Returns:
      str OR None: returns a list of arguments belonging to
        a tag, or returns None if no such arguments exist.

    Notes:
      Should also be handling complex kwargs, as well as args.

    """

    if ' ' in contents:
        # first arg is always the type of tag, e.g., func, inc
        __, args = contents.split(' ', 1)
        return args.split(' ')

    else:
        return None

