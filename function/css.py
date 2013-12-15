from lib import ini


CONFIG = {
          'replaces': 'css',
          'args': ['document'],
          'calls': 'css'
         }


def css(document, css_path):
    """Put the css file ((css derp.css)) in the header.

    """

    stylesheet = '<link href="%s" rel="stylesheet" type="text/css">\n</head>'
    return document.replace('</head>', stylesheet % css_path)
