#!/usr/local/bin/python

# modconf.py
# Lillian Lemmer <lillian.lynn.lemmer@gmail.com>
#
# This module is part of Sakura CMS and is released under the
# MIT license: http://opensource.org/licenses/MIT

"""sa-cli.py: Sakura CMS CLI interface

Usage:
  sa-cli.py --refresh
  sa-cli.py --setup
  sa-cli.py --httpd
  sa-cli.py --list
  sa-cli.py --backup
  sa-cli.py --install <snapshot_path>
  sa-cli.py --update <snapshot_path>
  sa-cli.py --info <snapshot_name>
  sa-cli.py --check <snapshot_path>
  sa-cli.py --delete <snapshot_name>
  sa-cli.py --snapshot <dest_path> <source_path> <source_path>...

"""

import sakura
import docopt

__VERSION__ = "0.9"


arguments = docopt.docopt(__doc__, version='sa-cli ' + __VERSION__)

# setup requried sakura directories
# should be ran after a fresh install
if arguments['--setup']:
    sakura.sakura.setup()

# snapshot install
# take the contents of a zip archive, extract it according to rules
if arguments['--install']:
    sakura.snapshot.install(arguments['<snapshot_path>'])

# snapshot update
# like install, but asks to overwrite... wait this isn't clear..
if arguments['--update']:
    sakura.snapshot.install(arguments['<snapshot_name>'], update=True)

# snapshot info
# display information about an installed snapshot
if arguments['--info']:
    sakura.snapshot.info(arguments['<snapshot_name>'])

# snapshot remove
if arguments['--delete']:
    sakura.snapshot.delete(arguments['<snapshot_name>'])

# create snapshot
if arguments['--snapshot']:
    sakura.snapshot.snapshot(arguments['<dest_path>'], *arguments['<source_path>'])

# snapshot check
# maybe call validate
if arguments['--check']:
    sakura.snapshot.check(arguments['<snapshot_path>'])

# rebuild cache
if arguments['--refresh']:
    sakura.sakura.cache()

# snapshot list
if arguments['--list']:
    sakura.snapshot.display_installed()

# built-in HTTP, CGI server
if arguments['--httpd']:
    sakura.sakura.httpd()

# backup
if arguments['--backup']:
    sakura.sakura.backup()

