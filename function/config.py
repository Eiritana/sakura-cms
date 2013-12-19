from sakura import common


SAKURA_ARGS =  ['document', 'element_full']


def config(document, replace, section, key):
    return document.replace(replace, common.SETTINGS[section][key])

