import getpass
import json
import os
from collections import OrderedDict

from django.core.management.base import BaseCommand
from django.utils.encoding import force_str

PROJECT_PATH = os.path.abspath(".")
CONFIG_DIR = os.path.join(PROJECT_PATH, 'config/')

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        actions = [self.configure_database, self.configure_celery, self.configure_dbbackup]
        i = 1
        max = len(actions)
        for a in actions:
            self.stdout.write("step: " + str(i) + "/" + str(max))
            a(*args, **options)
            self.stdout.write('\n')
            i += 1

    def configure_dbbackup(self, *args, **kwargs):
        self.stdout.write("<<==DBBackup Configuration==>>")
        backup_config_file = os.path.join(CONFIG_DIR, 'dbbackup_restore_config.py')
        if os.path.exists(backup_config_file):
            self.stdout.write("Already configured....skipping.")
        else:
            with open(CONFIG_DIR + 'dbbackup_restore_config.py', 'w') as f:
                f.write(open(CONFIG_DIR + 'dbbackup_restore_config.py.example', 'r').read())
            self.stdout.write("DBBackup configured successfully")

    def configure_celery(self, *args, **kwargs):
        self.stdout.write("<<==Celery Configuration==>>")
        celery_config_file = os.path.join(CONFIG_DIR, 'celery_config.py')
        if os.path.exists(celery_config_file):
            self.stdout.write("Already configured....skipping.")
        else:
            with open(CONFIG_DIR + 'celery_config.py', 'w') as f:
                f.write(open(CONFIG_DIR + 'celery_config.py.example', 'r').read())
            self.stdout.write("Celery configured successfully")

    def configure_database(self, *args, **kwargs):
        self.stdout.write("<<==Database Configuration==>>")
        db_config_file = os.path.join(CONFIG_DIR, 'database.py')
        if os.path.exists(db_config_file):
            answer = input("Already configured!!! Do you want to configure again? [Y/n] ")
            if answer.lower().startswith('y'):
                self._db_configuration(reconfigure=True)
        else:
            self._db_configuration()

    def _db_configuration(self, reconfigure=False):
        if reconfigure:
            from config.database import DATABASES
            default_db_name = DATABASES['default']['NAME']
            _db_name = input(force_str("Database Name (leave blank to use '" + default_db_name + "'): "))
            if default_db_name and _db_name.strip() == '':
                _db_name = default_db_name

            default_db_user = DATABASES['default']['USER']
            _db_user = input(force_str("User (leave blank to use '" + default_db_user + "'): "))
            if default_db_user and _db_user.strip() == '':
                _db_user = default_db_user

            default_db_password = DATABASES['default']['PASSWORD']
            _db_password = getpass.getpass(force_str("Password (leave blank to use '" + default_db_password + "'): "))
            if default_db_password and _db_password.strip() == '':
                _db_password = default_db_password

            default_db_host = DATABASES['default']['HOST']
            _db_host = input(force_str("Host (leave blank to use '" + default_db_host + "'): "))
            if default_db_host and _db_host.strip() == '':
                _db_host = default_db_host

            default_db_port = DATABASES['default']['PORT']
            _db_port = input(force_str("Port (leave blank to use '" + default_db_port + "'): "))
            if default_db_port and _db_port.strip() == '':
                _db_port = default_db_port

        else:
            _db_name = None
            while _db_name is None:
                _db_name = input(force_str('Database Name: '))
                if _db_name.strip() == '':
                    self.stderr.write("Error: Blank database name aren't allowed.")
                    _db_name = None
                    continue

            _db_user = None
            while _db_user is None:
                _db_user = input(force_str('User: '))
                if _db_name.strip() == '':
                    self.stderr.write("Error: Blank user aren't allowed.")
                    _db_user = None
                    continue

            _db_password = None
            while _db_password is None:
                _db_password = getpass.getpass(force_str('Password: '))
                if _db_password.strip() == '':
                    self.stderr.write("Error: Blank password aren't allowed.")
                    _db_password = None
                    continue

            _db_host = None
            while _db_host is None:
                _db_host = input(force_str('Host: '))
                if _db_host.strip() == '':
                    self.stderr.write("Error: Blank host aren't allowed.")
                    _db_host = None
                    continue

            _db_port = None
            while _db_port is None:
                _db_port = input(force_str('Port: '))
                if _db_port.strip() == '':
                    self.stderr.write("Error: Blank port aren't allowed.")
                    _db_port = None
                    continue

        with open(CONFIG_DIR + 'database.py', 'w') as f:
            code = CodeGenerator()
            code += "__author__ = '__auto_generated__'\n\n\n"
            code += 'DATABASES = '
            f.write(str(code))

            _default = OrderedDict()
            _default['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
            _default['NAME'] = _db_name
            _default['USER'] = _db_user
            _default['PASSWORD'] = _db_password
            _default['HOST'] = _db_host
            _default['PORT'] = _db_port
            db_config = {
                'default': _default
            }
            json.dump(db_config, f, indent=4, sort_keys=False, separators=(',', ': '))
        self.stdout.write("Database configured successfully")


class CodeGenerator:
    def __init__(self, indentation='\t'):
        self.indentation = indentation
        self.level = 0
        self.code = ''

    def indent(self):
        self.level += 1

    def dedent(self):
        if self.level > 0:
            self.level -= 1

    def __add__(self, value):
        temp = CodeGenerator(indentation=self.indentation)
        temp.level = self.level
        temp.code = str(self) + ''.join([self.indentation for i in range(0, self.level)]) + str(value)
        return temp

    def __str__(self):
        return str(self.code)
