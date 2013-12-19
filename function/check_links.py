"""Checks http status of all links"""


import httplib
from sakura.common import ini
from lxml import etree


SAKURA_ARGS =  ['document_path', 'document']


def check_links(document_path, document, nav_id):
    root = etree.HTML(document)
    __, document_path = document_path.split('/', 1)

    for element in root.iter('nav'):

        for link in element.iter('a'):
            href = link.attrib['href']

            if href == 'index.html':
                pass
            elif href[-10:] == 'index.html':
                href = href.replace('index.html', '')

            if document_path.startswith(href):
                link.attrib['id'] = 'active'

    return etree.tostring(root, pretty_print=True)


def status_check(host, path="/"):
    """Returns the status code of given URI"""

    try:
        conn = httplib.HTTPConnection(uri)
        conn.request('HEAD', path)
        return conn.getresponse().status

    except:
        return None

