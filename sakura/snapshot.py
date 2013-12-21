"""Sakura snapshot management.

Snapshots are simply archives of the sakura directory.

Useful for making "snapshots," backups, templates...

"""


import os
from zipfile import ZipFile, ZIP_DEFLATED
import sqlite3
import hashlib
import common as lib


def remote_install(path):
    # get file, put locally, set path
    snapshot_install(path)


def zip_file_index(zip_file):
    """Return a list of paths in zip_file."""

    is_sys_dir = lambda x: x.count('/') == 1 and x[-1] == '/'
    return [x for x in zip_file.namelist() if not is_sys_dir(x)]


def sanity_check(path):
    """Assure zip contents adhere to file structure standard.

    path (str) -- the path to the zip to perform a sanity check on

    Yields a two-element tuple, firest element is path, and second is "error."

    """

    zip_file = ZipFile(path, 'r')
    zip_index = zip_file_index(zip_file)
    zip_file.close()
    sane_directories = lib.SETTINGS['directories'].values()

    for path in zip_index:

        error = True
        path = path.split('/', 1)[0]

        if os.path.basename(path) in sane_directories:
            continue

        print 'unallowed basedir: ' + path


def check(path):
    """Used to check a snapshot before installing.
    
    Assure all files extract to any subdirectories of a sakura system
    directory, e.g., cgi/, functions/, content/.
    
    Maybe this should take a zipfile object; should also perform
    zip_file.testzip()

    """

    zip_file = ZipFile(path, 'r')
    print zip_file.comment
    crc_check = zip_file.testzip()
    zip_file.close()

    if crc_check:
        raise Exception(crc_check)
    else:
        print 'passed CRC and file check'

    sanity_check(path)

    return None


def file_checksum(path):
    """Generate a checksum to compare against later to detect
    file modification.

    """

    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def snapshot(snapshot_path, *paths):
    """Create an arcive, consisting of specified paths. Recursive.

    Appends comment for zip_file, as package data

    """

    zip_file = ZipFile(snapshot_path, 'a')
    zip_file.comment = 'unimplemented'  # will be implemented in the future

    for path in paths:

        if os.path.isfile(path):
            zip_file.write(path, path, ZIP_DEFLATED)
            continue

        # it's a directory, so recursively add files from a directory.
        for directory, files in lib.index(path).items():
            zip_file.write(directory, directory, ZIP_DEFLATED)

            for file_name in files:
                file_path = directory + '/' + file_name

                try:
                    zip_file.write(file_path, file_path, ZIP_DEFLATED)
                except:
                    # the timestamp preceeded 1980 for some reason
                    os.utime(file_path, None)
                    zip_file.write(file_path, file_path, ZIP_DEFLATED)

    zip_file.close()
    return None


def install(path, update=False):
    """snapshot zip-extraction protocol."""

    # sanity check
    for test_path, error in sanity_check(path):

        if error:
            print 'snapshot NOT SANE: ' + test_path
            return None

    # now open the archive...
    zip_file = ZipFile(path, 'r')
    zip_index = zip_file_index(zip_file)
    zip_file_name = path.rsplit('/', 1)[-1].replace('.zip', '')

    # setup database connection
    conn = sqlite3.connect('sakura.db')
    cursor = conn.cursor()

    # assure snapshot_files table exists...
    sql = '''\
          CREATE TABLE IF NOT EXISTS snapshot_files
          (
           path TEXT UNIQUE,
           snapshot TEXT,
           original_checksum TEXT UNIQUE
          )
          '''
    cursor.execute(sql)
    
    # assure snapshot_directories table exists...
    sql = '''
          CREATE TABLE IF NOT EXISTS snapshot_directories
          (
           path TEXT UNIQUE,
           snapshot TEXT
          )
          '''
    cursor.execute(sql)

    # assure snapshot_meta exists
    sql = '''\
          CREATE TABLE IF NOT EXISTS snapshot_meta
          (
           name TEXT UNIQUE,
           date_installed TEXT UNIQUE DEFAULT CURRENT_TIMESTAMP,
           error INTEGER DEFAULT 0
          )
          '''
    cursor.execute(sql)

    # insert record of install
    if not update:
        sql = 'INSERT INTO snapshot_meta (name) VALUES (?)'

        try:
            cursor.execute(sql, (zip_file_name,))
        except sqlite3.IntegrityError:
            print 'snapshot already installed: ' + zip_file_name
            return False


    # record files extracted...
    for path in zip_index:

        try:
            last_checksum = file_checksum(path)
        except IOError:
            pass

        if update:
            # if file was never modified, overwrite if update
            sql = '''\
                  SELECT original_checksum FROM snapshot_files
                  WHERE path=?
                  '''
            cursor.execute(sql, (path,))

            try:
                original_checksum = cursor.fetchone()[0]
            except TypeError:
                print '%s does not exist' % path
                #sys.exit(1)
                continue

            if last_checksum != original_checksum:
                question = 'replace modified file %s (y/n)? ' % path
                permission = raw_input(question)
                
                if permission == 'y':
                   pass
                else:
                    print 'skipping %s' % path
                    continue
            else:
                print "%s hasn't changed!" % path
                continue

        zip_file.extract(path)

        # test if directory
        try:
            new_checksum = file_checksum(path)

        except IOError:
            # can't create checksum for directory!
            # skip checksum stuff--custom sql here!
            sql = '''
                  INSERT INTO snapshot_directories (path, snapshot)
                  VALUES (?, ?)
                  '''
            cursor.execute(sql, (path, zip_file_name))
            continue

        sql = '''\
              INSERT INTO snapshot_files (path, snapshot, original_checksum)
              VALUES (?, ?, ?)
              '''

        try:
            cursor.execute(sql, (path, zip_file_name, new_checksum))
            conn.commit()  # in case install fails!

        except sqlite3.IntegrityError:
            print path + ' overwriten'

    zip_file.close()
    sql = 'UPDATE snapshot_meta SET error=0 WHERE name=?'
    cursor.execute(sql, (zip_file_name,))
    conn.commit()
    conn.close()
    return True


def display_installed():
    """Display installed snapshot information."""
    
    conn = sqlite3.connect('sakura.db')
    cursor = conn.cursor()
    sql = 'SELECT * FROM snapshot_meta'
    cursor.execute(sql)
    data = cursor.fetchall()
    conn.close()

    for name, date_installed, error in data:
        print 'NAME:      ' + name
        print 'INSTALLED: ' + date_installed
        print 'ERRORS:    ' + 'YES' if error else 'NO'
        print


def delete(name):
    """Delete file paths associated with snapshot."""

    conn = sqlite3.connect('sakura.db')
    cursor = conn.cursor()
    sql = 'SELECT path FROM snapshot_files WHERE snapshot=?'
    cursor.execute(sql, (name,))
    paths = cursor.fetchall()
    conn.close()

    if not paths:
        snapshot_error(name)

    # delete paths
    conn = sqlite3.connect('sakura.db')
    cursor = conn.cursor()

    for path in paths:
        path = path[0]

        try:
            os.remove(path)
        except OSError:
            print 'could not delete ' + path
            continue

        sql = 'DELETE FROM snapshot_files WHERE snapshot=? AND path=?'
        cursor.execute(sql, (name, path))
        conn.commit()  # incase deltion is interrupted

    # remove directories!
    sql = '''
          SELECT path FROM snapshot_directories WHERE snapshot=?
          ORDER BY LENGTH(path) DESC
          '''
    cursor.execute(sql, (name,))
    paths = cursor.fetchall()

    if not paths:
        snapshot_error(name)

    for path in paths:
        path = path[0]

        try:
            os.rmdir(path)
        except OSError:
            print 'could not delete ' + path
            continue

        sql = 'DELETE FROM snapshot_directories WHERE snapshot=? AND path=?'
        cursor.execute(sql, (name, path))
        conn.commit()

    # finish up! completely remove...
    sql = 'DELETE FROM snapshot_meta WHERE name=?'
    cursor.execute(sql, (name,))
    conn.commit()
    conn.close()
    return None


def error(snapshot):
    """This sucks. Should have proper exception?."""
    print 'no such snapshot "%s" installed' % snapshot
    sys.exit(1)


def info(snapshot):
    """Display files installed by "snapshot."
    
    Should also print snapshot_meta data.

    """

    conn = sqlite3.connect('sakura.db')
    cursor = conn.cursor()
    sql = 'SELECT path FROM snapshot_files WHERE snapshot=?'
    cursor.execute(sql, (snapshot,))
    file_paths = cursor.fetchall()
    conn.close()

    if not file_paths:
        snapshot_error(snapshot)

    # return file_paths

    for file_path in file_paths:
        print file_path[0]

