"""Do a lookup in the SETTINGS global.

{{func config httpd basehref}}

Will output the basehref defined in the [httpd] section of the
config/settings.ini file.

"""


from sakura import common


SAKURA_ARGS =  ['document', 'element_full']


def config(document, replace, section, key):
    return document.replace(replace, common.SETTINGS[section][key])

