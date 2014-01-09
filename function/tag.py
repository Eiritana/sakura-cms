"""Generate links and indexes for tags.

%%func tags some_tag another_tag%%

Notes:
  I hardcoded the value to the cache directory for generating tag link
  lists. Will solve in the future.

"""


from sakura import common
from cStringIO import StringIO
from bs4 import BeautifulSoup
from page_meta import page_meta
from sakura.common import ini
import sqlite3 as sqlite
import os


SAKURA_ARGS = ['document_path', 'document']  # i wanna rename document to contents
REPLACE_ALL = False


def tag(document_path, document, *args):
    conn = sqlite.connect('database/tag.db')
    cursor = conn.cursor()

    # because I like natural joins!
    sql = '''
          CREATE TABLE IF NOT EXISTS article (
            article_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            href TEXT NOT NULL UNIQUE
          );

          CREATE TABLE IF NOT EXISTS tag (
            tag_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
          );

          CREATE TABLE IF NOT EXISTS article_tag (
            article_id INTEGER REFERENCES article(id),
            tag_id INTEGER REFERENCES tag(id),

            PRIMARY KEY (article_id, tag_id)
          );
          '''
    cursor.executescript(sql)
    document_directory = os.path.dirname(document_path)  # NOT USED ELSEWHERE!
    settings = ini('blog_index')
    soup = BeautifulSoup(document)

    # article table: article_id, title, href
    title_element = soup.find(id=(settings['title']['id'],))

    try:
        title = title_element.contents[0]
    except:
        raise Exception(soup)

    href = document_path.split(os.path.sep, 1)[-1]
    sql = 'INSERT INTO article (title, href) VALUES (?, ?)'
    cursor.execute(sql, (title, href))

    # assure tags in db
    # yes, this is typically faster than attempting to convert args to a list
    # of tuplesand using executemany
    for tag in args:
        cursor.execute('INSERT OR IGNORE INTO tag (name) VALUES (?)', (tag,))

    # link tabs to article in db
    sql = 'SELECT article_id FROM article WHERE href=?'
    cursor.execute(sql, (href,))
    article_id = cursor.fetchone()[0]
    tag_list = ['<ul class="tag-list">']

    for tag in args:
        sql = '''
              INSERT INTO article_tag (article_id, tag_id)
              VALUES (?, (SELECT tag_id FROM tag WHERE name=?))
              '''
        cursor.execute(sql, (article_id, tag))
        entry = '<li><a href="/cache/index_%s.html">%s</a></li>' % (tag, tag)
        tag_list.append(entry)

    conn.commit()
    conn.close()
    tag_list.append('</ul>')
    return '\n'.join(tag_list)

