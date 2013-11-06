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


def parse_plugins(public):
    package = 'plugins'
    plugins = {}

    for file_name in glob('plugins/*.py'):
        module_name = file_name.split('/', 1)[1].replace('.py', '')

        if module_name == "__init__":
            continue

        # setup the plugin entry
        plugin_config = __import__("plugins.%s" % (module_name), fromlist=["CONFIG"])
        plugin_config = plugin_config.CONFIG
        replaces = plugin_config['replaces']
        args = [public[arg] for arg in plugin_config['args']]
        calls = plugin_config['calls']
        func = __import__("plugins.%s" % (module_name), fromlist=[calls])
        func = getattr(func, calls)
        plugins[replaces] = (func, args)

    return plugins


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
        func, args = parse_plugins(public)[element['name']]

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
    content_directory = lib.SETTINGS['directories']['content']

    date_time = datetime.now().isoformat()
    backup_directory += '/' + date_time + '/'
    os.mkdir(backup_directory)

    # make specified backups
    backups = lib.SETTINGS['backups']
    pending_backups = [k for k,v in backups.items() if v == 'yes']

    for directory in pending_backups:
        archive_path = backup_directory + directory
        shutil.make_archive(archive_path, 'zip', directory)


class ThreadingCGIServer(SocketServer.ThreadingMixIn,
                   BaseHTTPServer.HTTPServer):

    pass


def httpd():
    handler = CGIHTTPServer.CGIHTTPRequestHandler
    handler.cgi_directories = ['/cgi']
    server = ThreadingCGIServer(('', 8080), handler)

    try:
        while 1:
            sys.stdout.flush()
            server.handle_request()

    except KeyboardInterrupt:
        print "Finished"


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
elif args.refresh:
    cache()
elif args.httpd:
    httpd()
elif args.backup:
    backup()
else:
    parser.print_help()

