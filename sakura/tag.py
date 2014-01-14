import re


TAG_LEFT = '##'
TAG_RIGHT = '##'

TAG_INCLUDE_LEFT = '##inc '
TAG_INCLUDE_RIGHT = '##'

TAG_FUNCTION_LEFT = '##func '
TAG_FUNCTION_RIGHT = '##'

TAG_VARIABLE_LEFT = '##var '
TAG_VARIABLE_RIGHT = '##'


class Tag(object):

    def __init__(self, contents):
        self.full = contents
        self.contents = contents[len(TAG_LEFT):-len(TAG_RIGHT)]
        self.tag_type = contents[len(TAG_LEFT):].split(' ', 1)[0]
        self.action = contents.split(' ', 2)[1].replace(TAG_RIGHT, '')
        self.attribs = get_attributes(contents)
        self.args = self.contents.split(' ')[2:]

    def __getitem__(self, key):
        return self.attribs[key]

    def __iter__(self):
        return iter(self.attribs)

    def items(self):

        for key, value in self.attribs.items():
            yield key, value


class TagDoc(object):
    """An interface for selecting Sakura markup data."""

    def __init__(self, source=None, path=None):
        self.source = source
        self.path = path

        if path and source is None:

            with open(path) as f:
                self.source = f.read()

    def __contains__(self, key):
        return self.has(key)

    def has(self, tag):
        """Return True if tags with bracket types exist, else false.

        Args:
          tag (str) -- the kind of ##tag## to search for

        Returns:
          bool: True if Sakura tags are present in string, False otherwise.

        """

        return bool(re.search(pattern(tag), self.source))

    def __nonzero__(self):
        return bool(self.source)

    def __iter__(self):
        return self.find('any', self.source, attributes=True)

    def __str__(self):
        return self.source

    def iter_while(self, tag_type='all'):
        """Yield tags of tag type until there are none left in source.

        """

        while self.has(tag_type):

            for tag in self.find(tag_type):
                yield tag

    def find(self, tag_type='all', *args, **kwargs):
        """Iterate over tags with defined attribute names.

        Args:
          tag_type (str, optional): see the pattern.
          *args: strings of attribute names
          **kwargs: attribute=value to match

        Yields:
            dict: tag information, i.e., full, contents, name, attribs

        """

        tag_pattern =  pattern(tag_type)

        # define the required attribute names for matching
        if args:
            attribute_names = args
        elif kwargs:
            attribute_names = kwargs.keys()
        else:
            attribute_names = None


        for match in re.finditer(tag_pattern, self.source):
            tag = Tag(match.group(0))

            # comparison checks
            if attribute_names:

                # if all appropriate attribute names are in the
                # tag's attributes
                if all([a in tag for a in args]):

                    if kwargs:
                        # attribute == value

                        if all([tag[k] == kwargs[k] for k in kwargs]):
                            yield tag
                        else:
                            continue

                else:
                    continue

            yield tag

    def __call__(self, tag_type='all', *args, **kwargs):
        """Find is the most useful feature I see..."""
        return self.find(tag_type=tag_type, *args, **kwargs)

    def first(self, tag_type='all', *args, **kwargs):
        """Return the tag dictionary of the first tag/element with
        the specified attribute name.

        Args:
          tag_type (str, optional): the name of the kind of tag
            you want to search through.
          *args: strings of the attribute names to match

        Returns:
            dict|None: tag dictionary; None if no such tag found

        Notes:
          Needs more elaboration...

        """

        for tag in self.find(tag_type, *args, **kwargs):
            return tag

        return None

    def replace(self, find_this, replace_with):
        self.source = self.source.replace(find_this, replace_with)


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
                           'all': (TAG_LEFT, TAG_RIGHT),
                          }[tag]
    return  tag_left + '(.*)' + tag_right


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


