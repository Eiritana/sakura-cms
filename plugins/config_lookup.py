import lib


CONFIG = {
          'replaces': 'config',
          'args': ['document', 'element_full'],
          'calls': 'config_lookup'
         }


def config_lookup(document, replace, section, key):
    return document.replace(replace, lib.SETTINGS[section][key])

