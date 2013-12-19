"""Tools for parsing a document.

"""


import re
from cStringIO import StringIO
import common as lib
import func


def iter_tags(tag, document):
    """Yields a dictionary of data for the current "tag" in iteration.

    tag (str) -- the name of the element. %%tag%%
    document (str) -- iterate tag in this document

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
    
    tag (str) -- the kind of %%tag%% to search for
    document (str) -- the document to search in
    
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
    
    Not sure if it should be a %%func%%.
    
    """

    __, file_extension = os.path.splitext(document_path)
    file_extension = file_extension.replace('.', '')
    document = document.strip()

    if file_extension in ('html', 'css'):
        document = document.replace('  ', ' ').replace('\n', '')

    return document


def include(document, include_directory):
    """Replaces instances of %%inc *.*%% with the contents of a plaintext file.
    
    Example: %%inc foo.txt%% would be replaced by the file contents of
    include/foo.txt.
    
    document (str) -- document being parsed
    include_directory (str) -- this is just the include directory
    
    """

    # full element, element contents, and element name!
    for element in iter_tags('inc', document):
        include_tag = element['name']
        path = include_directory + '/' + include_tag

        # retrieve file specified in %%inc%% call
        with open(path) as f:
            include = f.read().strip()

        # use attributes as replacements; %%substitutions%%
        attribute_pattern = (
                             """(\S+)=["']?((?:.(?!["']?\s+"""
                             """(?:\S+)=|[>"']))+.)["']?"""
                            )

        for match in re.finditer(attribute_pattern, element['full']):
            value = match.group(2)
            key = '%%var ' + match.group(1) + '%%'
            include = include.replace(key, value)

        document = document.replace(element['full'], include)

    return document


def parse(document_path):
    """Sakura element function, returns string.
    
    Parse a document in CONTENT; then parse named variables
    sent to that include, if available.

    document_path (str) -- path of file being parsed
    
    """

    include_directory = lib.SETTINGS['directories']['include']

    # the primary document content
    with open(document_path) as f:
        document = f.read().strip()

    # while includes still exist, call them!
    # this solves the problem of having an include in an include.
    while tag_type_exists('inc', document):
        document = include(document, include_directory)

    # replace ((functions)) -- importantly last
    for element in iter_tags('func', document):

        # we need to test for existing args
        if ' ' in element['contents']:
            __, args = element['contents'].split(' ', 1)
            user_defined_args = args.split(' ')

        else:
            user_defined_args = None

        # room for elaboration on this...
        public = {
                  'document_path': document_path,
                  'document': document,
                  'element_full': element['full'],
                  'element_name': element['name'],
                 }

        try:
            function, args = func.load_functions(public)[element['name']]
        except KeyError:
            error_vars = (document_path, element['name'], element['full'])
            print '%%func%%    %s: %s is not loaded (%s)' % error_vars
            continue

        # if we do have user defined arguments in the element,
        # then append them to the args!
        if user_defined_args:
            args.extend(user_defined_args)

        data = function(*args)

        if user_defined_args:
            document = data.replace(element['full'], '')
        else:
            document = document.replace(element['full'], data)

    if lib.SETTINGS['parser']['minify'] == 'yes':
        document = minify(document_path, document)

    return document

