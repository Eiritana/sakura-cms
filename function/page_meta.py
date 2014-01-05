"""Generate HTML which states the time which the document was modified and
created.

"""


from sakura.common import ini
import os.path, time


SAKURA_ARGS =  ['document_path']
REPLACE_ALL = False


def page_meta(path):
    """Document statistics HTML."""

    modified = time.ctime(os.path.getmtime(path))
    created = time.ctime(os.path.getctime(path))
    meta = (
            '<strong>Last modified:</strong> %s<br>'
            '\n<strong>Created:</strong> %s'
            % (modified, created)
           )
    meta_settings = ini('page_meta')['general']
    open_tag = meta_settings['open_tag']
    close_tag = meta_settings['close_tag']
    return open_tag + meta + close_tag

