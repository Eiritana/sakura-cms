"""Common utilities used across multiple modules.

Configuration file management, index generation.

"""

import ConfigParser
from collections import OrderedDict
import os
import inspect


def ini(path):
    """Loads an INI file into a dictionary.

    Args:
      path (str): the filename/path of the .ini config file to read,
        relative to config/.

    Returns:
      dict: nested-dictionary representation of an INI file.
        Top-level keys being sections, nested dictionary being
        the actual key=value pairs.

    """

    parsed_config = {}

    # use os.path
    config_file_name = path + '.ini'
    path = os.path.normpath(os.path.join('config', config_file_name))

    with open(path) as f:
        config = ConfigParser.ConfigParser()
        config.readfp(f)

        for k,v in config._sections.items():

            if v.get('var'):
                del v['var']

            if v['__name__']:
                del v['__name__']

            parsed_config[k] = v

    return parsed_config


def index(directory=None):
    """Create an index of directories and files.
    
    Returns a dictionary, where the key is the dirpath and the value is
    a tuple of files.

    Args:
      directory (str, optional): the directory (and its contents)
        to index; the path. Defaults to the content directory.

    Returns:
      dict: { 'content/resources/': ('file.txt', 'derp.txt', 'foo.html') }

    """

    settings = ini('settings')
    directory = directory or settings['directories']['content']
    index_d = OrderedDict()

    for dirpath, __, filenames in os.walk(directory):
        index_d[dirpath] = filenames

    return index_d

