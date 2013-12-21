#!/usr/local/bin/python
"""Sakura CLI interface"""


import sakura
import argparse


description = (
               'Sakura content management system; parses files, then "caches" '
               'them.'
              )
function = argparse.ArgumentParser(description=description, prog='sa-cli')

refresh_help = 'Clear CACHE and reparse CONTENT into CACHE.'
function.add_argument(
                    '--refresh',
                    help=refresh_help,
                    dest='refresh',
                    action='store_true'
                   )

setup_help = 'Setup Sakura directories.'
function.add_argument(
                    '--setup',
                    help=setup_help,
                    dest='setup',
                    action='store_true'
                   )

# built-in HTTP, CGI server
httpd_help = 'Start HTTPD server.'
function.add_argument(
                    '--httpd',
                    help=httpd_help,
                    dest='httpd',
                    action='store_true'
                   )

# snapshot install
install_help = 'Install a snapshot (.zip)'
function.add_argument(
                      '--install',
                      help=install_help,
                     )

# snapshot info
info_help = 'Display files belonging to a snapshot.'
function.add_argument(
                    '--info',
                    help=info_help
                   )

# snapshot update
update_help = 'Update a snapshot by name.'
function.add_argument(
                    '--update',
                    help=update_help
                   )

# snap snapshot
snapshot_help = 'Add a series of paths to a snapshot, recursively.'
function.add_argument(
                    '--snapshot',
                    nargs='+',
                    help=snapshot_help
                   )

# snapshot
snapshot_help = 'Make a snapshot (also useful for backups'
function.add_argument(
                      '--snapshot',
                      help=snapshot_help,
                     )

# snapshot check
check_help = 'Check a snapshot before you install it!'
function.add_argument(
                    '--check',
                    help=check_help
                   )

# snapshot remove
delete_help = 'Delete a snapshot (by name)'
function.add_argument(
                    '--delete',
                    help=delete_help,
                   )

# snapshot list
list_help = 'List installed snapshot'
function.add_argument(
                    '--list',
                    help=list_help,
                    dest='list',
                    action='store_true'
                   )

# backup
backup_help = 'Backup defined Sakura directories.'
function.add_argument(
                    '--backup',
                    help=backup_help,
                    dest='backup',
                    action='store_true'
                   )

# add --restore
args = function.parse_args()

if args.setup:
    setup()
elif args.install:
    sakura.snapshot.install(args.install)
elif args.update:
    sakura.snapshot.install(args.update, update=True)
elif args.info:
    sakura.snapshot.info(args.info)
elif args.delete:
    sakura.snapshot.delete(args.delete)
elif args.snapshot:
    sakura.snapshot.snapshot(*args.insert)
elif args.check:
    sakura.snapshot.check(args.check)
elif args.refresh:
    sakura.sakura.cache()
elif args.list:
    sakura.snapshot.display_installed()
elif args.httpd:
    sakura.sakura.httpd()
elif args.backup:
    sakura.sakura.backup()
else:
    function.print_help()

