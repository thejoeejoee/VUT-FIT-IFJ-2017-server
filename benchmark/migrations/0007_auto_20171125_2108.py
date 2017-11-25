# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-25 20:08
from __future__ import unicode_literals

import os

from django.db import migrations
from django.db.migrations.operations.special import RunSQL


def load_sql(filename):
    with open(os.path.join(os.path.dirname(__file__), 'sql/', '{}.sql'.format(filename))) as f:
        return f.read()

class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0006_auto_20171121_2218'),
    ]

    operations = [
        RunSQL(load_sql('0007'), load_sql('0007'))
    ]
