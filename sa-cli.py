#!/usr/local/bin/python
"""Sakura CLI interface"""


from sakura import sakura
import argparse


description = (
               'Sakura content management system; parses files, then "caches" '
               'them.'
              )
function = argparse.ArgumentParser(description=description, prog='sakura')

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

# plugin install
install_help = 'Install a plugin (.zip)'
function.add_argument(
                      '--install',
                      help=install_help,
                     )

# plugin info
info_help = 'Display files belonging to a plugin.'
function.add_argument(
                    '--info',
                    help=info_help
                   )

# plugin update
update_help = 'Update a plugin by name.'
function.add_argument(
                    '--update',
                    help=update_help
                   )

# plugin insert
insert_help = 'Add a series of paths to a plugin, recursively.'
function.add_argument(
                    '--insert',
                    nargs='+',
                    help=insert_help
                   )

# plugin check
check_help = 'Check a plugin before you install it!'
function.add_argument(
                    '--check',
                    help=check_help
                   )

# plugin remove
delete_help = 'Delete a plugin (by name)'
function.add_argument(
                    '--delete',
                    help=delete_help,
                   )

# plugin list
list_help = 'List installed plugins'
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
    sakura.plugin.install(args.install)
elif args.update:
    sakura.plugin.install(args.update, update=True)
elif args.info:
    sakura.plugin.info(args.info)
elif args.delete:
    sakura.plugin.delete(args.delete)
elif args.insert:
    sakura.plugin.insert(*args.insert)
elif args.check:
    sakura.plugin.check(args.check)
elif args.refresh:
    sakura.cache()
elif args.list:
    sakura.plugin.display_installed()
elif args.httpd:
    sakura.httpd()
elif args.backup:
    sakura.backup()
else:
    function.print_help()

