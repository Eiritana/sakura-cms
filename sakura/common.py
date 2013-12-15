import ConfigParser
from collections import OrderedDict
import os
import inspect


def ini(path):
    """Loads an INI file into a dictionary."""

    parsed_config = {}

    path = 'config/' + path + '.ini'

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
    
    Returns a dictionary, where the key is the dirpath and the value is a
    tuple of files.
    
    """

    settings = ini('settings')
    directory = directory or settings['directories']['content']
    index_d = OrderedDict()

    for dirpath, __, filenames in os.walk(directory):
        index_d[dirpath] = filenames

    return index_d


SETTINGS = ini('settings')

if SETTINGS['directories']['basehref'] == 'scriptpath':
    SETTINGS['directories']['basehref'] = os.path.abspath(inspect.getfile(inspect.currentframe())).rsplit('/', 1)[0] + '/' + SETTINGS['directories']['cache'] + '/'

