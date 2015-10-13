#!/usr/bin/env python

import os
import sys
import time
import django

sys.path.insert(0, './tests')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_test')


def create_extension_postgis():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('CREATE EXTENSION IF NOT EXISTS postgis')


if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    try:
        create_extension_postgis()
    except django.db.utils.OperationalError:
        time.sleep(10)  # Occasionally the Postgres container doesn't boot quickly enough.
        create_extension_postgis()

    args = sys.argv
    args.insert(1, 'test')

    if len(args) == 2:
        args.insert(2, 'tests')

    execute_from_command_line(args)
