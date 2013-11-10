from lib import ini


CONFIG = {
          'replaces': 'breadcrumbs',
          'args': ['document_path'],
          'calls': 'breadcrumbs'
         }


def breadcrumbs(path):
    """A piece function, which generates breadcrumbs."""

    bcrumbs_settings = ini('breadcrumbs')['general']
    crumbs = path.split('/')
    del crumbs[0]  # this would be the content directory

    if len(crumbs) == 1:
        return ''

    home_href = bcrumbs_settings['home_href']
    home_text = bcrumbs_settings['home_text']
    breadcrumb = ['<a href="%s">%s</a>' % (home_href, home_text)]
    current_directory = ''

    for crumb in crumbs:

        if crumb == 'index.html':
            # preceeding was a directory, no need to specify index file
            break

        # we first assume it's a file...
        crumb_link = current_directory + crumb

        if '.' not in crumb:
            # this crumb is a directory!
            current_directory += crumb + '/'
            crumb_link = current_directory + 'index.html'

        crumb_label = crumb.rsplit('.', 1)[0]
        crumb_label = crumb_label.replace('-', ' ').replace('_', ' ').title()
        breadcrumb.append('<a href="%s">%s</a>' % (crumb_link, crumb_label))

    breadcrumb = ' &gt; '.join(breadcrumb)
    open_tag = bcrumbs_settings['open_tag']
    close_tag = bcrumbs_settings['close_tag']
    return open_tag + '\n<p>' + breadcrumb + '\n</p>\n' + close_tag

