from sakura.common import ini
from lxml import etree


SAKURA_ARGS = ['document_path', 'document']


def nav_active(document_path, document, nav_id):
    """Marks a link therein #nav_id, if it's the document we're parsing."""

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

