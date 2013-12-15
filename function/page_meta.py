from sakura.lib import ini
import os.path, time


CONFIG = {
          'replaces': 'document-meta',
          'args': ['document_path'],
          'calls': 'page_meta'
         }


def page_meta(path):
    """Document statistics HTML."""

    modified = time.ctime(os.path.getmtime(path))
    created = time.ctime(os.path.getctime(path))
    meta = (
            '<strong>Last modified:</strong> %s<br>'
            '\n<strong>Created:</strong> %s'
            % (modified, created)
           )
    meta_settings = ini('document-meta')['general']
    open_tag = meta_settings['open_tag']
    close_tag = meta_settings['close_tag']
    return open_tag + meta + close_tag

