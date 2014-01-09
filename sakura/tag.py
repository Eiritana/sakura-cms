import re


TAG_LEFT = '##'
TAG_RIGHT = '##'

TAG_INCLUDE_LEFT = '##inc '
TAG_INCLUDE_RIGHT = '##'

TAG_FUNCTION_LEFT = '##func '
TAG_FUNCTION_RIGHT = '##'

TAG_VARIABLE_LEFT = '##var '
TAG_VARIABLE_RIGHT = '##'


def pattern(tag):
    """Returns the regular expression for the specified tag.

    Args:
      tag (str): one of: function, include, or variable.

    Returns:
      str: regular expression for matching specified tag.

    """

    tag_left, tag_right = {
                           'include': (TAG_INCLUDE_LEFT, TAG_INCLUDE_RIGHT),
                           'function': (TAG_FUNCTION_LEFT, TAG_FUNCTION_RIGHT),
                           'variable': (TAG_VARIABLE_LEFT, TAG_VARIABLE_RIGHT),
                           'any': (TAG_LEFT, TAG_RIGHT),
                          }[tag]
    return  tag_left + '(.*)' + tag_right


def iter_tags(tag, document, attributes=False):
    """Yields a dictionary of data for the current "tag" in iteration.

    Args:
      tag (str): the name of the element. ##tag##
      document (str): iterate tag in this document
      attributes (bool): if true, add an attributes dictionary
        to the dictionary yielded.

    Yields:
      dict: "full" tag being substituted (##func blah blah##)
        the "contents" of said tag (func blah blah), and the "name" of
        the tag (func).

    Examples:
      >>> document = '##func foo## ##var bar## ##inc foo.txt## ##func bar##'
      >>> [element['name'] for element in iter_tags('func', document)]
      ['foo', 'bar']

    Notes:
      Will probably rename to tag_iter.
      Will make document first arg.

    """

    tag_pattern =  pattern(tag)

    for match in re.finditer(tag_pattern, document):
        full_element = match.group(0)  # inc. the brackets
        element_contents = match.group(1)  # exclude brackets
        element_name = element_contents.split(' ', 1)[0]

        tag = {
               'full': full_element,
               'contents': element_contents,
               'name': element_name,
              }

        if attributes:
            tag.update({'attribs': get_attributes(tag['full'])})

        yield tag


def iter_attribute(document, tag_type, attribute_name):

    for tag in iter_tags(tag_type, document):
        tag_attributes = get_attributes(tag['contents'])

        if attribute_name in tag_attributes:
            yield tag, tag_attributes


def from_attribute(document, tag_type, attribute_name, attribute_value):
    """Seek out a unique attribute name, value combination
    and returnthat tag.

    Args:
      document (str): document contents
      tag_type (str): the tag type which to search through
      attribute_name (str): the attribute name to match
      attribute_value (str): the attribute value to match

    Returns:
      dict|None: Typical tag dictionary. Returns None if no match

    """

    for tag, attributes in iter_attribute(document, tag_type, attribute_name):

        if attributes[attribute_name] == attribute_value:
            return tag, attributes

    return None, None


def get_attributes(full_tag):
    """Return attributes belonging to the octothrope contents.

    Args:
      full_tag: the full octothorpe, e.g., ##func tag derp##

    Returns:
      dict: attributes, by name: value.

    Examples:
      >>> tag_attributes('##inc head.txt title="something"##')
      {'title': 'something'}
      >>> tag_attributes("##inc head.txt title='something'##")
      {'title': 'something'}
      >>> tag_attibutes("inc head.txt title='something'")
      {'title': 'something'}

    Notes:
      I may separate tag functions to a tag module.

    """

    pattern = """(\S+)=["']?((?:.(?!["']?\s+""""""(?:\S+)=|[>"']))+.)["']?"""
    return {m.group(1): m.group(2) for m in re.finditer(pattern, full_tag)}


def exists(tag, document):
    """Return True if tags with bracket types exist, else false.

    Args:
      tag (str) -- the kind of ##tag## to search for
      document (str) -- the document to search in

    Returns:
      bool: True if Sakura tags are present in string, False otherwise.

    Examples:
      >>> document = 'blah ##inc foo.txt## blah blah ##func bar##'
      >>> tag_exists('func', document)
      True

      >>> tag_exists('var', document)
      False

    """

    return bool(re.search(pattern(tag), document))

