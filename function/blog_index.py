"""blog index globs current directory to list snippets of each
article therein.

"""


from sakura import common
from cStringIO import StringIO
import re
from page_meta import page_meta
from sakura.common import ini
from sakura import tag
from bs4 import BeautifulSoup


SAKURA_ARGS = ['document_path']
REPLACE_ALL = False


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

    # summary
    summary_open = settings['summary']['open']
    summary_close = settings['summary']['close']

    for directory, files in index_d.items():
        paths = [directory + '/' + fname for fname in files]

        # determine category somehow?
        # raise Exception(directory)

        for path in paths:

            if path.endswith('index.html'):
                continue

            with open(path) as f:
                article = f.read()

            # get the article title, permalink
            # get title from octothorpe ##code##
            element = tag.TagDoc(article).first('include', 'title')
            title = element['title']

            # assemble the obtained data
            contents.write(container_open)
            contents.write(header_open)
            link = path.split('/', 1)[-1]
            contents.write('  ' + permalink % (link, title))

            # get meta
            contents.write(page_meta(path))
            contents.write(header_close)

            # get the first paragraph after the article title
            # I'll have to grab the first paragraph from the article path
            for paragraph in BeautifulSoup(article).find_all('p'):
                paragraph = paragraph.string

                if element.full in paragraph:
                    continue

            paragraph = (
                         summary_open
                         + paragraph
                         + summary_close
                        )
            contents.write(paragraph)
            contents.write(container_close)

    return contents.getvalue()

