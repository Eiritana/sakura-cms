"""Use to go over cache and "optimize" files for search engines, as well
as speed in general.

  * inserts canonical links in headers

"""

from sakura.common import SETTINGS
from lxml import etree


SAKURA_ARGS = ['document_path', 'document']


def seo(document_path, document):
    """Inserts canonical to header, other stuff..."""

    basehref = SETTINGS['httpd']['basehref']
    href = basehref + document_path
    canonical = '<link rel="canonical" href="%s" />' % href
    #raise Exception(document.replace('</head>', canonical + '\n</head>'))
    return document.replace('</head>', canonical + '\n</head>')

