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

    settings = lib.ini('settings')

    try:
        cache_directory = settings['directories']['cache']

        if settings['backups']['before_cache'] == 'yes':
            backup()

        shutil.rmtree(cache_directory)

    except IOError:  # this is friggin' awful; except what?!
        pass

    os.mkdir(cache_directory)


def cache():
    """Completely parse all viable files therein the content directory, to the
    cache directory.

    """

    flush_cache()
    settings = lib.ini('settings')
    content_dir = settings['directories']['content']
    cache_dir = settings['directories']['cache']

    for working_directory, file_names in lib.index().items():
        # first we remove the base (usually content) directory
        baseless_directory_list = working_directory.split(os.path.sep)[1:]
        baseless_directory = os.path.sep.join(baseless_directory_list)

        # if there are directories in path, then we need to create them
        if len(baseless_directory_list) > 0:
            output_directory = os.path.join(cache_dir, baseless_directory)
            os.mkdir(output_directory)
        else:
            output_directory = cache_dir

        for file_name in file_names:
            # join the current file name to the current directory (sans base)
            # then join that with
            baseless_file_path = os.path.join(baseless_directory, file_name)
            content_file_path = os.path.join(content_dir, baseless_file_path)
            cache_file_path = os.path.join(output_directory, file_name)

            if file_name in ('_cache', '_generate'):
                # in the future this will be for exceptions for file names
                # and file types we want to skip parsing and just copy over

                with open(content_file_path) as f:
                    cached_contents = f.read()

            else:
                # parse!
                cached_contents = parse.parse(baseless_file_path)

            with open(cache_file_path, 'w') as f:

                try:
                    f.write(cached_contents)
                except TypeError:
                    raise Exception((cache_file_path, cached_contents))

    recache()
    parse.cache_generate()
    return None


def recache():
    """Finally, go over the cached/refreshed contents therein the cache
    directory and apply functions to each.

    What the hell is this even for, again? Isn't this cache_generate()?

    """

    settings = lib.ini('settings')
    cache_dir = settings['directories']['cache']

    for directory_path, file_names in lib.index(cache_dir).items():
        directories = directory_path.split(os.path.sep)[1:]
        new_directory = cache_dir

        if len(directories) > 0:
            new_dirs = os.path.sep.join(directories)
            new_directory = os.path.join(new_directory, new_dirs)

        for file_name in file_names:
            file_path = os.path.join(directory_path, file_name)
            cached_file_path = os.path.join(new_directory, file_name)
            cached_file = parse.parse_cache(file_path)

            with open(cached_file_path, 'w') as f:
                f.write(cached_file)

    return None


def setup():
    """Lazy installer; it sets up the directory
    structure for Sakura.

    """

    settings = lib.ini('settings')

    for directory_type, directory_path in settings['directories'].items():

        try:
            os.mkdir(directory_path)

        except OSError:
            print directory_type + ' already exists'


def backup():
    """Zip the config and content directories into a backup/date
    folder.

    """

    settings = lib.ini('settings')
    backup_directory = settings['directories']['backups']
    date_time = datetime.now().isoformat()
    backup_directory = os.path.join(backup_directory, date_time)
    os.mkdir(backup_directory)

    # get the directories to backup, plus a setting
    backup_conf = settings['backups'].copy()
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
    """THIS IS A TOY. It is only here so users may test parsed
    contents before making them public.

    """

    settings = lib.ini('settings')
    address = settings['httpd']['address']
    port = int(settings['httpd']['port'])
    handler = CGIHTTPServer.CGIHTTPRequestHandler
    handler.cgi_directories = ['/cgi']
    server = ThreadingCGIServer((address, port), handler)

    try:

        while 1:
            sys.stdout.flush()
            server.handle_request()

    except KeyboardInterrupt:
        print "Finished"

