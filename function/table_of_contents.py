from sakura.common import ini
from lxml import etree
from cStringIO import StringIO


SAKURA_ARGS = ['document_path', 'document']


def table_of_contents(document_path, document):
    """Maybe instead of StringIO I should build with lxml?

    """

    table_settings = ini('table-of-contents')
    root = etree.HTML(document)  # can define base_url!
    headings = ('h3', 'h4', 'h5', 'h6')
    current_level = -1
    current_level_text = None
    html = StringIO()

    # heading
    open_tag = table_settings['heading']['open_tag']
    close_tag = table_settings['heading']['close_tag']
    text = table_settings['heading']['text']
    html.write(open_tag + text + close_tag)

    # start table of contents... table
    html.write(table_settings['container']['open_tag'])
    __, document_path = document_path.split('/', 1)
    number_of_entries = 0

    for element in root.iter():
        tag = element.tag

        if tag not in headings:
            continue

        number_of_entries += 1
        nest_level = headings.index(tag)
        level_id =  element.get('id')
        level_text = element.text

        if level_id:
            entry = '<a href="%s#%s">%s</a>' % (document_path, level_id, level_text)
        else:
            entry = level_text

        if nest_level == current_level:
            html.write('<li>%s' % entry)
        elif nest_level > current_level:
            html.write('\n<ol>\n <li>%s' % entry)
        elif nest_level < current_level:
            html.write('</ol>\n <li>%s' % entry)

        current_level = nest_level

    if number_of_entries < 2:
        return ''

    html.write('\n</ol>')
    html.write(table_settings['container']['close_tag'])
    return html.getvalue()

