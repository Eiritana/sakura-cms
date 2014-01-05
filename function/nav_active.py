"""Sets link's ID as "active", if it's within the specified navigation ID and
it's href matches the current document's being parsed.

"""


from sakura.common import ini
from bs4 import BeautifulSoup
import os


SAKURA_ARGS = ['document_path', 'document']
REPLACE_ALL = True


def nav_active(document_path, document, nav_id):
    """Marks a link therein #nav_id, if it's the document we're parsing."""

    __, file_extension = os.path.splitext(document_path)

    if file_extension not in ('.html', '.htm'):
        return document

    __, document_path = document_path.split('/', 1)
    soup = BeautifulSoup(document)
    navigation = soup.find_all("nav", id=(nav_id,))

    for element in navigation:

        for link in element.find_all('a'):
            href = link.get('href')

            if href == 'index.html':
                pass
            elif href[-10:] == 'index.html':
                href = href.replace('index.html', '')

            if document_path.startswith(href):
                link['id'] = 'active'
                link.replace_with(link)

    return str(soup.encode('utf-8'))

