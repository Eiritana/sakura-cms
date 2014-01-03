"""blog index globs current directory to list snippets of each
article therein.

"""


from sakura import common
from cStringIO import StringIO
from bs4 import BeautifulSoup
from page_meta import page_meta
from sakura.common import ini


SAKURA_ARGS = ['document_path']


def blog_index(document_path):
    settings = ini('blog_index')
    document_directory, __ = document_path.rsplit('/', 1)
    contents = StringIO()  # being replaced
    index_d = common.index(document_directory)
    truncate = 50
    
    # title/permalink
    open_tag = settings['title']['open']
    close_tag = settings['title']['close']
    permalink = open_tag + '<a href="%s">%s</a>' + close_tag

    # container
    container_open = settings['container']['open']
    container_close = settings['container']['close']

    # header
    header_open = settings['header']['open']
    header_close = settings['header']['close']

    for directory, files in index_d.items():
        paths = [directory + '/' + fname for fname in files]

        # determine category somehow?
        # raise Exception(directory)

        for path in paths:

            with open(path) as f:
                article = f.read()

            # get the article title, permalink
            soup = BeautifulSoup(article)
            title_element = soup.find(id=(settings['title']['id'],))
            title = title_element.contents[0]
            contents.write(container_open)
            contents.write(header_open)
            link = path.split('/', 1)[-1]
            contents.write('  ' + permalink % (link, title))

            # get meta
            contents.write(page_meta(path))
            contents.write(header_close)

            # get the first paragraph after the article title
            paragraph = str(title_element.findNextSibling('p'))
            contents.write(paragraph)
            contents.write(container_close)

    return contents.getvalue()

