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

    settings = lib.ini('settings')
    include_directory = settings['directories']['include']

    # this is so messy I want to vomit out of my eye sockets
    # Possibility to parse inclusions within inclusions.
    # the iterator should be in a while loop itself!
    for element in document.iter_while('include'):
        include_tag = element.action
        path = os.path.join(include_directory, include_tag)

        # retrieve file specified in ##inc## call
        try:

            with open(path) as f:
                include = f.read().strip()

        except IOError:
            raise IncludeError(path, document.path)

        # Includes are able to reference the attributes from the
        # respective include-octothorpe.
        # ##var title## will return "wag" from ##inc title='wag'##
        for attribute_name, attribute_value in element.items():
            octothorpe_variable = (
                                   tag.TAG_VARIABLE_LEFT
                                   + attribute_name
                                   + tag.TAG_VARIABLE_RIGHT
                                  )
            include = include.replace(octothorpe_variable, attribute_value)

        document.replace(element.full, include)

    return document.source


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

    # temporary, will lookup in settings in the future
    document_path = os.path.join('content', document_path)
    document = tag.TagDoc(path=document_path)

    if not document:
        raise Exception(document.source)

    include(document)
    function.replace(document)

    return document.source


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


    path = os.path.join('cache', '_cache')
    function_list = tag.TagDoc(path=path)
    function_list.path = document_path

    if function_list is None:
        return None

    with open(document_path) as f:
        edit_contents = f.read()

    return function.replace(function_list, edit_this=edit_contents)


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

    path = os.path.join('cache', '_generate')
    function_list = tag.TagDoc(path=path)

    if function_list is None:
        return None

    return function.replace(function_list, no_return=True)

