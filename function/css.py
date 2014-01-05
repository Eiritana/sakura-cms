"""Link the specified stylesheet to the document in the <head>."""


from sakura.common import ini


SAKURA_ARGS =  ['document']
REPLACE_ALL = True


def css(document, css_path):
    stylesheet = '<link href="%s" rel="stylesheet" type="text/css">\n</head>'
    return document.replace('</head>', stylesheet % css_path)
