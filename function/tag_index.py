"""Generate links and indexes for tags.

%%func tags some_tag another_tag%%

"""


from sakura import common
from cStringIO import StringIO
from bs4 import BeautifulSoup
from page_meta import page_meta
from sakura.common import ini
import sqlite3 as sqlite


SAKURA_ARGS = []
REPLACE_ALL = True


def tag_index():
    conn = sqlite.connect('database/tag.db')
    conn.text_factory = str
    cursor = conn.cursor()
    sql = '''
          SELECT * FROM article_tag
          NATURAL JOIN tag
          NATURAL JOIN article
          ORDER BY tag_id
          '''
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()

    # build html
    last_tag_name = None
    indexes = {}  # will contain tag_name: StringIO()

    for row in rows:

        # (1, 1, u'sakura', u'Sakura 0.1', u'blog/sakura/sakura-0.1.html')
        tag_name = row[2]
        article_title = row[3]
        href = row[4]

        if last_tag_name not in (tag_name, None):
            indexes[last_tag_name].write('</ul>')

            with open('cache/index_' + tag_name + '.html', 'w') as f:
                f.write(indexes[last_tag_name].getvalue())

        if tag_name not in indexes:
            indexes[tag_name] = StringIO()
            indexes[tag_name].write('<ul>')

        entry = '<li><a href="%s">%s</a></li>' % (href, article_title)
        indexes[tag_name].write(entry)
        last_tag_name = tag_name

    indexes[tag_name].write('</ul>')

    for tag_name, index_contents in indexes.items():

        with open('cache/index_' + tag_name + '.html', 'w') as f:
            f.write(index_contents.getvalue())

    return None

