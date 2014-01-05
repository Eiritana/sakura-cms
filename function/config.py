"""Do a lookup in the SETTINGS global.

{{func config httpd basehref}}

Will output the basehref defined in the [httpd] section of the
config/settings.ini file.

"""


from sakura import common


SAKURA_ARGS =  ['document', 'element_full']
REPLACE_ALL = True


def config(document, replace, section, key):
    settings = common.ini('settings')
    return document.replace(replace, settings[section][key])

