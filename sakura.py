#!/usr/local/bin/python
"""Parses files in the content directory."""


import os
import sys
import re
import shutil
import argparse
from cStringIO import StringIO
from datetime import datetime
from lxml import etree
import lib
from glob import glob
import SocketServer
import BaseHTTPServer
import CGIHTTPServer
from zipfile import ZipFile
import sqlite3
import hashlib


# CONFIG AND CONSTANTS ########################################################


ATTRIBUTE_PATTERN = """(\S+)=["']?((?:.(?!["']?\s+(?:\S+)=|[>"']))+.)["']?"""


###############################################################################


def iter_tags(open_bracket, close_bracket, document):
    pattern = open_bracket + '(.*)' + close_bracket

    for match in re.finditer(pattern, document):
        full_element = match.group(0)  # inc. the brackets
        element_contents = match.group(1)  # exclude brackets
        element_name = element_contents.split(' ', 1)[0]

        yield {
               'full': full_element,
               'contents': element_contents,
               'name': element_name
              }


def tag_type_exists(open_bracket, close_bracket, document):
    """Return True if tags with bracket types exist, else false."""

    pattern = open_bracket + '(.*)' + close_bracket

    if re.search(pattern, document):
        return True

    else:
        return False


def minify(document_path, document):
    """Compress CSS and HTML mostly by removing whitespace."""

    document_type = document_path.rsplit('.', 1)[-1]
    document = document.strip()

    if document_type in ('html', 'css'):
        document = document.replace('  ', ' ').replace('\n', '')

    return document


def calls_piece(document, piece_directory):
    """Replaces/parses {{piece}} calls."""

    # replace {{piece}} calls
    # full element, element contents, and element name!
    for element in iter_tags('{{', '}}', document):
        piece_tag = element['contents'].split(' ', 1)[0]
        path = piece_directory + '/' + piece_tag

        # retrieve file specified in {{piece}} call
        with open(path) as f:
            piece = f.read().strip()

        # use attributes as replacements; %%substitutions%%
        for match in re.finditer(ATTRIBUTE_PATTERN, element['full']):
            value = match.group(2)
            key = '%%' + match.group(1) + '%%'
            piece = piece.replace(key, value)

        document = document.replace(element['full'], piece)

    return document


def load_parsers(public):
    package = 'parsers'
    parsers = {}

    for file_name in glob(package + '/*.py'):
        module_name = file_name.split('/', 1)[1].replace('.py', '')

        if module_name == "__init__":
            continue

        # setup the plugin entry
        parser_path = "%s.%s" % (package, module_name)
        parser_config = __import__(parser_path, fromlist=["CONFIG"])
        parser_config = parser_config.CONFIG
        replaces = parser_config['replaces']
        args = [public[arg] for arg in parser_config['args']]
        calls = parser_config['calls']
        func = __import__(parser_path, fromlist=[calls])
        func = getattr(func, calls)
        parsers[replaces] = (func, args)

    return parsers


def parse(document_path):
    """Sakura element parser, returns string.
    
    Parse a document in CONTENT; then parse named variables
    sent to that piece, if available.

    document_path (str) -- path of file being parsed
    
    """

    piece_directory = lib.SETTINGS['directories']['pieces']

    # the primary document content
    with open(document_path) as f:
        document = f.read().strip()

    # while pieces still exist, call them!
    # this solves the problem of having a piece in a piece.
    while tag_type_exists('{{', '}}', document):
        document = calls_piece(document, piece_directory)

    # replace ((functions)) -- importantly last
    for element in iter_tags('\(\(', '\)\)', document):

        # we need to test for existing args
        if ' ' in element['contents']:
            __, args = element['contents'].split(' ', 1)
            user_defined_args = args.split(' ')
        else:
            user_defined_args = None

        public = {
                  'document_path': document_path,
                  'document': document,
                  'element_full': element['full'],
                  'element_name': element['name'],
                 }
        func, args = load_parsers(public)[element['name']]

        # if we do have user defined arguments in the element,
        # then append them to the args!
        if user_defined_args:
            args.extend(user_defined_args)

        data = func(*args)

        if user_defined_args:
            document = data.replace(element['full'], '')
        else:
            document = document.replace(element['full'], data)

    if lib.SETTINGS['parser']['minify'] == 'yes':
        document = minify(document_path, document)

    return document


def flush_cache():
    """Returns True if cache was "flushed."

    """

    try:
        cache_directory = lib.SETTINGS['directories']['cache']

        if lib.SETTINGS['backups']['before_cache'] == 'yes':
            backup()

        shutil.rmtree(cache_directory)

    except:
        pass

    os.mkdir(cache_directory)


def cache():
    flush_cache()
    content_dir = lib.SETTINGS['directories']['content']
    cache_dir = lib.SETTINGS['directories']['cache']

    for directory_path, file_names in lib.index().items():

        directories = directory_path.split('/')[1:]

        # keep trailing slash!
        new_directory = cache_dir + '/' 

        if len(directories) > 0:
            new_directory += '/'.join(directories) + '/'

            # make directory
            os.mkdir(new_directory)

        for file_name in file_names:
            file_path = directory_path + '/' + file_name
            cached_file_path = new_directory + file_name
            cached_file = parse(file_path)

            with open(cached_file_path, 'w') as f:
                f.write(cached_file)


def setup():

    for directory_type, directory_path in lib.SETTINGS['directories'].items():

        try:
            os.mkdir(directory_path)

        except OSError:
            print directory_type + ' already exists'


def backup():
    """Zip the config and content directories into a backup/date folder

    """

    backup_directory = lib.SETTINGS['directories']['backups']

    date_time = datetime.now().isoformat()
    backup_directory += '/' + date_time + '/'
    os.mkdir(backup_directory)

    # gleem settings first...
    backup_conf = lib.SETTINGS['backups'].copy()
    backup_conf.pop('before_cache')

    # make specified backups
    pending_backups = [k for k,v in backup_conf.items() if v == 'yes']

    for directory in pending_backups:
        archive_path = backup_directory + directory
        shutil.make_archive(archive_path, 'zip', directory)


class ThreadingCGIServer(SocketServer.ThreadingMixIn,
                   BaseHTTPServer.HTTPServer):

    pass


def httpd():
    address = lib.SETTINGS['httpd']['address']
    port = int(lib.SETTINGS['httpd']['port'])
    handler = CGIHTTPServer.CGIHTTPRequestHandler
    handler.cgi_directories = ['/cgi']
    server = ThreadingCGIServer((address, port), handler)

    try:
        while 1:
            sys.stdout.flush()
            server.handle_request()

    except KeyboardInterrupt:
        print "Finished"


def plugin_remote_install(path):
    # get file, put locally, set path
    plugin_install(path)


def zip_file_index(zip_file):
    is_sys_dir = lambda x: x.count('/') == 1 and x[-1] == '/'
    return [x for x in zip_file.namelist() if not is_sys_dir(x)]


def plugin_check(path):
    """Used to check a plugin before installing.
    
    Assure all files extract to any subdirectories of a sakura system
    directory, e.g., cgi/, parsers/, content/.
    
    """

    zip_file = ZipFile(path, 'r')
    zip_index = zip_file_index(zip_file)
    zip_file.close()

    for path in zip_file_index(zip_file):
        print path

    return None


def file_checksum(path):

    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def plugin_install(path, update=False):
    """Plugin zip-extraction protocol."""

    zip_file = ZipFile(path, 'r')
    zip_index = zip_file_index(zip_file)
    zip_file_name = path.rsplit('/', 1)[-1].replace('.zip', '')

    # create a temporary directory to work in
    # os.makedir('tmp')

    # setup database connection
    conn = sqlite3.connect('sakura.db')
    cursor = conn.cursor()

    # assure plugin_files table exists...
    sql = '''\
          CREATE TABLE IF NOT EXISTS plugin_files
          (
           path TEXT UNIQUE,
           plugin TEXT,
           original_checksum TEXT UNIQUE
          )
          '''
    cursor.execute(sql)
    # keep md5 checksum of file after extracting for updates
    # do not overwrite files that have a changed md5

    # assure plugin_meta exists
    sql = '''\
          CREATE TABLE IF NOT EXISTS plugin_meta
          (
           name TEXT UNIQUE,
           date_installed TEXT UNIQUE DEFAULT CURRENT_TIMESTAMP,
           sane INTEGER DEFAULT 0
          )
          '''
    cursor.execute(sql)

    # insert record of install
    if not update:
        sql = 'INSERT INTO plugin_meta (name) VALUES (?)'
        cursor.execute(sql, (zip_file_name,))


    # record files extracted...
    for path in zip_index:

        try:
            last_checksum = file_checksum(path)
        except IOError:
            pass

        zip_file.extract(path)
        new_checksum = file_checksum(path)

        if update:
            # if file was never modified, overwrite if update
            sql = '''\
                  SELECT original_checksum FROM plugin_files
                  WHERE path=?
                  '''
            cursor.execute(sql, (path,))
            original_checksum = cursor.fetchone()[0]
            # raise Exception((last_checksum, original_checksum))

            if last_checksum != original_checksum:
                question = 'replace modified file %s (y/n)? ' % path
                permission = raw_input(question)
                
                if permission == 'y':
                    pass
                else:
                    pass

        sql = '''\
              INSERT INTO plugin_files (path, plugin, original_checksum)
              VALUES (?, ?, ?)
              '''

        try:
            cursor.execute(sql, (path, zip_file_name, new_checksum))
            conn.commit()  # in case install fails!

        except sqlite3.IntegrityError:
            print path + ' overwriten'

    zip_file.close()

    sql = 'UPDATE plugin_meta SET sane=1 WHERE name=?'
    cursor.execute(sql, (zip_file_name,))
    conn.commit()
    conn.close()


def plugin_delete(name):
    """Delete file paths associated with plugin."""

    conn = sqlite3.connect('sakura.db')
    cursor = conn.cursor()
    sql = 'SELECT path FROM plugin_files WHERE plugin=?'
    cursor.execute(sql, (name,))
    paths = cursor.fetchall()
    conn.close()

    if not paths:
        plugin_error(name)

    # delete paths
    conn = sqlite3.connect('sakura.db')
    cursor = conn.cursor()

    for path in paths:
        path = path[0]

        try:
            os.remove(path)
        except OSError:
            'could not delete ' + path

        sql = 'DELETE FROM plugin_files WHERE plugin=? AND path=?'
        cursor.execute(sql, (name, path))
        conn.commit()  # incase deltion is interrupted

    sql = 'DELETE FROM plugin_meta WHERE name=?'
    cursor.execute(sql, (name,))
    conn.commit()
    conn.close()
    return None


def plugin_list():
    pass


def plugin_error(plugin):
    print 'no such plugin "%s" installed' % plugin
    sys.exit(1)


def plugin_info(plugin):
    """Display files installed by "plugin."
    
    Should also print plugin_meta data.

    """

    conn = sqlite3.connect('sakura.db')
    cursor = conn.cursor()
    sql = 'SELECT path FROM plugin_files WHERE plugin=?'
    cursor.execute(sql, (plugin,))
    file_paths = cursor.fetchall()
    conn.close()

    if not file_paths:
        plugin_error(plugin)

    # return file_paths

    for file_path in file_paths:
        print file_path[0]


# COMMAND LINE USAGE ##########################################################


description = (
               'Sakura content management system; parses files, then "caches" '
               'them.'
              )
parser = argparse.ArgumentParser(description=description, prog='sakura')

refresh_help = 'Clear CACHE and reparse CONTENT into CACHE.'
parser.add_argument(
                    '--refresh',
                    help=refresh_help,
                    dest='refresh',
                    action='store_true'
                   )

setup_help = 'Setup Sakura directories.'
parser.add_argument(
                    '--setup',
                    help=setup_help,
                    dest='setup',
                    action='store_true'
                   )

# built-in HTTP, CGI server
httpd_help = 'Start HTTPD server.'
parser.add_argument(
                    '--httpd',
                    help=httpd_help,
                    dest='httpd',
                    action='store_true'
                   )

# plugin install
install_help = 'Install a plugin (.zip)'
parser.add_argument(
                    '--install',
                    help=install_help,
                   )

# plugin info
info_help = 'Display files belonging to a plugin.'
parser.add_argument(
                    '--info',
                    help=info_help
                   )

# plugin update
update_help = 'Update a plugin by name.'
parser.add_argument(
                    '--update',
                    help=update_help
                   )

# plugin check
check_help = 'Check a plugin before you install it!'
parser.add_argument(
                    '--check',
                    help=check_help
                   )

# plugin remove
delete_help = 'Delete a plugin (by name)'
parser.add_argument(
                    '--delete',
                    help=delete_help,
                   )

# plugin list
list_help = 'List installed plugins'
parser.add_argument(
                    '--list',
                    help=list_help,
                    dest='list',
                    action='store_true'
                   )

# backup
backup_help = 'Backup defined Sakura directories.'
parser.add_argument(
                    '--backup',
                    help=backup_help,
                    dest='backup',
                    action='store_true'
                   )

# add --restore
args = parser.parse_args()

if args.setup:
    setup()
elif args.install:
    plugin_install(args.install)
elif args.update:
    plugin_install(args.update, update=True)
elif args.info:
    plugin_info(args.info)
elif args.delete:
    plugin_delete(args.delete)
elif args.check:
    plugin_check(args.check)
elif args.refresh:
    cache()
elif args.httpd:
    httpd()
elif args.backup:
    backup()
else:
    parser.print_help()

