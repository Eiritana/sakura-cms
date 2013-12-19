from sakura import common
from cStringIO import StringIO
from lxml import etree
from page_meta import page_meta


SAKURA_ARGS =  ['document_path']


def blog_index(document_path):
    """((blog-index)) globs current directory to list snippets of each
    article therein.

    Includes links!

    """

    document_directory, __ = document_path.rsplit('/', 1)
    contents = StringIO()  # being replaced
    index_d = common.index(document_directory)
    truncate = 50
    permalink = '<h3><a href="%s">%s</a></h3>'

    for directory, files in index_d.items():
        paths = [directory + '/' + fname for fname in files]

        # determine category somehow?
        # raise Exception(directory)

        for path in paths:

            with open(path) as f:
                article = f.read()

            root = etree.fromstring(article, parser=etree.HTMLParser())

            # get the article title, permalink
            title = root.xpath("//*[@id='article-title']")[0].text
            contents.write('<section>\n')
            contents.write(' <header>\n')
            link = path.split('/', 1)[-1]
            contents.write('  ' + permalink % (link, title))

            # get meta
            contents.write(page_meta(path))
            contents.write('\n</header>\n')

            # get the first paragraph after the article title
            # lxml for some reason includes outlying content/invalid HTML
            # i.e., ((my)) {{dear markup}}.
            s = root.xpath("//*[@id='article-title']/following-sibling::*")
            paragraph = etree.tostring(s[0]).rsplit('</p>', 1)[0] + '</p>'
            contents.write(paragraph)
            contents.write('</section>')

    return contents.getvalue()

