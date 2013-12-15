from lib import ini
from lxml import etree


CONFIG = {
          'replaces': 'nav-active',
          'args': ['document_path', 'document'],
          'calls': 'nav_active'
         }


def nav_active(document_path, document, nav_id):
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

