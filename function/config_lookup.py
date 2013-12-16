from sakura import common


CONFIG = {
          'replaces': 'config',
          'args': ['document', 'element_full'],
          'calls': 'config_lookup'
         }


def config_lookup(document, replace, section, key):
    return document.replace(replace, common.SETTINGS[section][key])

