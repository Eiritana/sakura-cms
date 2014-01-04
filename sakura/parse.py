"""Tools for parsing a document.

Notes: just like the element dictionary I should have a document dictionary,
which includes document and document path.

"""


import re
from cStringIO import StringIO
import common as lib
import func


def iter_tags(tag, document):
    """Yields a dictionary of data for the current "tag" in iteration.

    Args:
      tag (str): the name of the element. %%tag%%
      document (str): iterate tag in this document

    Yields:
      dict: "full" tag being substituted (%%func blah blah%%),
      the "contents" of said tag (func blah blah), and the "name" of
      the tag (func).

    >>> document = '%%func foo%% %%var bar%% %%inc foo.txt%% %%func bar%%'
    >>> [element['name'] for element in iter_tags('func', document)]
    ['foo', 'bar']

    """

    pattern = '%%' + tag + ' (.*)%%'

    for match in re.finditer(pattern, document):
        full_element = match.group(0)  # inc. the brackets
        element_contents = match.group(1)  # exclude brackets
        element_name = element_contents.split(' ', 1)[0]

        yield {
               'full': full_element,
               'contents': element_contents,
               'name': element_name
              }


def tag_type_exists(tag, document):
    """Return True if tags with bracket types exist, else false.

    Args:
      tag (str) -- the kind of %%tag%% to search for
      document (str) -- the document to search in

    Returns:
      bool: True if Sakura tags are present in string, False otherwise.

    >>> document = 'blah %%inc foo.txt%% blah blah %%func bar%%'
    >>> tag_type_exists('func', document)
    True
    >>> tag_type_exists('var', document)
    False

    """

    pattern = '%%' + tag + ' (.*)%%'
    return True if re.search(pattern, document) else False


def minify(document_path, document):
    """Compress CSS and HTML mostly by removing whitespace.

    Args:
      document_path (str): path to file to be "minimized"
      document (str): the contents of said document

    Returns:
      str: whitespace-reduced version of the document arg.

    Notes:
      Not sure if it should be a %%func%% for _cache.

    >>> minify('foo.html', '  what   ')
    'what '

    """

    __, file_extension = os.path.splitext(document_path)
    file_extension = file_extension.replace('.', '')
    document = document.strip()

    if file_extension in ('html', 'css'):
        document = document.replace('  ', ' ').replace('\n', '')

    return document


def include(document):
    """Returns the document contents, after making the file inclusion
    substitution.

    Replaces instances of %%inc *.*%% with the contents of a plaintext
    file. For example %%inc foo.txt%% would be replaced by the file
    contents of include/foo.txt.

    Args:
      document (dict): document dictionary for the document being parsed

    Returns:
      str: document contents with other file contents included;
        specified in inclusion tags--therein document['contents'].

    """

    contents = document['contents']

    # while includes still exist, call them!
    # this solves the problem of having an include in an include.
    settings = lib.ini('settings')
    include_directory = settings['directories']['include']

    while tag_type_exists('inc', contents):

        # full element, element contents, and element name!
        for element in iter_tags('inc', contents):
            include_tag = element['name']
            path = include_directory + '/' + include_tag

            # retrieve file specified in %%inc%% call
            with open(path) as f:
                include = f.read().strip()

            # use attributes as replacements; %%substitutions%%
            # reading aloud will summon cthulu, etc.
            attribute_pattern = (
                                 """(\S+)=["']?((?:.(?!["']?\s+"""
                                 """(?:\S+)=|[>"']))+.)["']?"""
                                )

            for match in re.finditer(attribute_pattern, element['full']):
                value = match.group(2)
                key = '%%var ' + match.group(1) + '%%'
                include = include.replace(key, value)

            contents = contents.replace(element['full'], include)

    return contents


def replace_functions(document):
    """Replace Sakura functions %%func function-name args%%.

    Used for parsing the function list _cache, which specified functions to
    use on every document therein cache.

    Args:
      document (dict): the document being evaluated
        to find the functions.
      edit (str): the document to place the evaluation
        of the function in.

    Returns:
      str: the version of the document contents, with the function
        tag calls evaluated and substituted.

    """

    contents = document['contents']
    document_path = document['path']
    edit_contents = document.get('edit_contents', None)
    new_contents = edit_contents or contents

    # replace ((functions)) -- importantly last
    for element in iter_tags('func', contents):
        new_contents = evaluate_function(
                                         element,
                                         new_contents,
                                         document_path,
                                         debug=edit_contents
                                        )

    return new_contents


def evaluate_function(element, contents, document_path, debug=False):
    """Take a given Sakura %%func%% element, and return the contents
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
        function, args = func.load_functions(public)[element['name']]
    except KeyError:
        error_vars = (document_path, element['name'], element['full'])
        raise Exception('%%func%%    %s: %s is not loaded (%s)' % error_vars)

    # if we do have user defined arguments in the element,
    # then append them to the args!
    if user_defined_args:
        args.extend(user_defined_args)

    data = function(*args)

    if debug:
        return data

    if user_defined_args:
        return data.replace(element['full'], '')
    else:
        return contents.replace(element['full'], data)


def parse(document_path):
    """Sakura element function, returns string.
    
    Parse a document in CONTENT; then parse named variables
    sent to that include, if available.
    
    A document dictionary is generated and passed around quite a bit from
    here out.

    Args:
      document_path (str): path of file being parsed

    Returns:
      str: parsed/evaluated/substituted version of the contents
        belonging to the file specified in document_path.
    
    """

    # the primary document content
    document = {'path': document_path}

    with open(document['path']) as f:
        document['contents'] = f.read().strip()

    document['contents'] = include(document)

    # replace ((functions)) -- importantly last
    document = replace_functions(document)
    settings = lib.ini('settings')

    if settings['parser']['minify'] == 'yes':
        document = minify(document_path, document)

    return document


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


def parse_cache(document_path):
    """Parse the cached document with a sakura function.

    Args:
      document_path (str) -- path of file being parsed

    Returns:
      dict: the document (from document_path): contents...
      WILL ELABORATE LATER

    Notes:
      Has a hardcoded value (function_list), bad!

    """

    function_list = 'cache/_cache'

    with open(function_list) as f:
        function_list = f.read()

    with open(document_path) as f:
        edit_contents = f.read()

    document = {
                'contents': function_list,
                'edit_contents': edit_contents,
                'path': document_path
               }
    return replace_functions(document)

