#!/usr/local/bin/python
"""Parses files in the content directory."""


import os
import sys
import shutil
from datetime import datetime
import common as lib
import SocketServer
import BaseHTTPServer
import CGIHTTPServer
import parse


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
    """Completely parse all viable files therein the content directory, to the
    cache directory.
    
    """

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
            cached_file = parse.parse(file_path)

            with open(cached_file_path, 'w') as f:
                f.write(cached_file)


def setup():
    """Lazy installer; it sets up the directory
    structure for Sakura.

    """

    for directory_type, directory_path in lib.SETTINGS['directories'].items():

        try:
            os.mkdir(directory_path)

        except OSError:
            print directory_type + ' already exists'


def backup():
    """Zip the config and content directories into a backup/date folder"""

    backup_directory = lib.SETTINGS['directories']['backups']
    date_time = datetime.now().isoformat()
    backup_directory += '/' + date_time + '/'
    os.mkdir(backup_directory)

    # get the directories to backup, plus a setting
    backup_conf = lib.SETTINGS['backups'].copy()
    backup_conf.pop('before_cache')  # not a directory to backup!

    # make specified backups
    pending_backups = [k for k,v in backup_conf.items() if v == 'yes']

    for directory in pending_backups:
        archive_path = backup_directory + directory
        shutil.make_archive(archive_path, 'zip', directory)


# HTTP Daemon/Testing Tool ####################################################


class ThreadingCGIServer(SocketServer.ThreadingMixIn,
                   BaseHTTPServer.HTTPServer):

    pass


def httpd():
    """THIS IS A TOY. It is only here so users may test parsed contents before
    making them public.

    """

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

