import os
import re
import shutil
import unittest

import osgtest.library.core as core
import osgtest.library.files as files
import osgtest.library.service as service
import osgtest.library.osgunittest as osgunittest

class TestStartMySQL(osgunittest.OSGTestCase):


    def test_01_backup_mysql(self):
        core.skip_ok_unless_installed('mysql-server', 'mysql')
        core.config['mysql.backup'] = False
        
        if not core.options.backupmysql:
            return

        # Find the folder where the mysql files are stored
        pidfile = '/var/run/mysqld/mysqld.pid'
        if not os.path.exists(pidfile):
            service.start('mysqld', sentinel_file=pidfile) # Need mysql up to determine its datadir

        command = ('mysql', '-e', "SHOW VARIABLES;")
        mysql_cfg = core.check_system(command, 'dump mysql config')[0].strip().split("\n")
        print(mysql_cfg)
        for line in mysql_cfg:
            try:
                core.config['mysql.datadir'] = re.match('datadir\s*([\w\/]*)\/$', line).group(1)
            except AttributeError, e:
                if e.args[0] == "'NoneType' object has no attribute 'group'":
                    # No match was found, move onto the next line
                    continue
                else:
                    raise
            else:
                break

        # Backup the old mysql folder
        service.stop('mysqld') 
        backup = core.config['mysql.datadir'] + '-backup'
        try:
            shutil.move(core.config['mysql.datadir'], backup)
        except OSError:
            # Folder doesn't exist so we don't have to worry about backups
            pass
        else:
            core.config['mysql.backup'] = backup

    def test_02_start_mysqld(self):
        core.skip_ok_unless_installed('mysql-server')
        service.start('mysqld', sentinel_file='/var/run/mysqld/mysqld.pid')

