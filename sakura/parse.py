"""Tools for parsing a document.

Notes: just like the element dictionary I should have a document dictionary,
which includes document and document path.

"""


import os
import re
from cStringIO import StringIO
import common as lib
import function
import tag


def from_dir(directory, file_path, path=False):
    """Return the contents of a file therein the config-specified
    directory.

    Args:
      file_path (str): the filepath/filename, relative to
        the cache directory.

      path (str): if True return the new path as well

    Returns:
      str|tuple: contents of file, or a tuple containing both the
        contents and the new file path

    """

    settings = lib.ini('settings')
    cache_dir = settings['directories'][directory]
    file_path = os.path.join(cache_dir, file_path)

    try:

        with open(file_path) as f:

            contents = f.read()

            if path:
                return (contents, file_path)
            else:
                return contents

    except IOError:
        raise Exception(file_path)

        if path:
            return (None, None)
        else:
            return None


class IncludeError(Exception):
    def __init__(self, path, current_document_path):
        message = (
                   '%s does not exist (inclusion on %s)'
                   % (path, current_document_path)
                  )
        Exception.__init__(self, message)


def include(document):
    """Returns the document contents, after making the file inclusion
    substitution.

    Replaces instances of ##inc *.*## with the contents of a plaintext
    file. For example ##inc foo.txt## would be replaced by the file
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

    while tag.exists('include', contents):

        # full element, element contents, and element name!
        for element in tag.iter_tags('include', contents):
            include_tag = element['name']
            path = os.path.join(include_directory, include_tag)

            # retrieve file specified in ##inc## call
            try:

                with open(path) as f:
                    include = f.read().strip()

            except IOError:
                raise IncludeError(path, document['path'])

            # Includes are able to reference the attributes from the
            # respective include-octothorpe.
            # ##var title## will return "wag" from ##inc title='wag'##
            attributes = tag.attributes(element['full'])

            for attribute_name, attribute_value in attributes.items():
                octothorpe_variable = (
                                       tag.TAG_VARIABLE_LEFT
                                       + attribute_name
                                       + tag.TAG_VARIABLE_RIGHT
                                      )
                include = include.replace(octothorpe_variable, attribute_value)

            contents = contents.replace(element['full'], include)

    return contents


def parse(document_path):
    """Sakura element function, returns string.
    
    Parse a document in CONTENT; then parse named variables
    sent to that include, if available.
    
    A document dictionary is generated and passed around quite a bit from
    here out.

    Args:
      document_path (str): path of file being parsed

    Returns:
      str: document dictionary: path, contents.

    """

    document = {}
    document['contents'], path = from_dir('content', document_path, path=True)
    document['path'] = path

    if document['contents'] is None:
        raise Exception(document)

    document['contents'] = include(document)
    document = function.replace(document)

    return document


def parse_cache(document_path):
    """Parse the cached document with a sakura function.

    I use this while iterating through files in the cache,
    as this will perform all of the functions therein
    _cache, on the document_path in question.

    Args:
      document_path (str) -- path of file being parsed

    Returns:
      dict|None: the document (from document_path): contents...
        Returns None if there is no _cache file.

    """


    function_list = from_dir('cache', '_cache')

    if function_list is None:
        return None

    with open(document_path) as f:
        edit_contents = f.read()

    document = {
                'contents': function_list,
                'edit_contents': edit_contents,
                'path': document_path
               }
    return function.replace(document)


def cache_generate():
    """Generate files based on functions therein _generate.

    This is the last thing to run while caching.

    These kinds of functions are totally independent from
    document-specific data.

    Returns:
        str: document contents

    Notes:
      Shares A LOT with parse_cache...

    """

    function_list = from_dir('cache', '_generate')

    if function_list is None:
        return None

    document = {
                'contents': function_list,
                'no_return': True,
                'path': function_list
               }
    return function.replace(document)

