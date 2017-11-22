# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-21 17:44
from __future__ import unicode_literals

from django.db import migrations
from django.db.migrations.operations.special import RunSQL

_sql = """
ALTER TABLE benchmark_result
  ALTER COLUMN id TYPE UUID USING id :: UUID;

ALTER TABLE benchmark_resultauthor
  DROP CONSTRAINT IF EXISTS benchmark_resultauthor_team_id_fkey;
ALTER TABLE benchmark_resultauthor
  ALTER COLUMN team_id TYPE UUID USING team_id :: UUID;
ALTER TABLE benchmark_team
  ALTER COLUMN id TYPE UUID USING id :: UUID;
ALTER TABLE benchmark_resultauthor
  ADD CONSTRAINT benchmark_resultauthor_team_id_fkey
FOREIGN KEY (team_id) REFERENCES benchmark_team;


ALTER TABLE benchmark_result
  DROP CONSTRAINT IF EXISTS benchmark_result_test_case_id_fkey;
ALTER TABLE benchmark_result
  DROP CONSTRAINT IF EXISTS benchmark_result_author_id_fkey;
ALTER TABLE benchmark_result
  ALTER COLUMN test_case_id TYPE UUID USING test_case_id :: UUID;
ALTER TABLE benchmark_result
  ALTER COLUMN author_id TYPE UUID USING author_id :: UUID;
ALTER TABLE benchmark_testcase
  ALTER COLUMN id TYPE UUID USING id :: UUID;
ALTER TABLE benchmark_resultauthor
  ALTER COLUMN id TYPE UUID USING id :: UUID;
ALTER TABLE benchmark_result
  ADD CONSTRAINT benchmark_result_test_case_id_fkey
FOREIGN KEY (test_case_id) REFERENCES benchmark_testcase;
ALTER TABLE benchmark_result
  ADD CONSTRAINT benchmark_result_author_id_fkey
FOREIGN KEY (author_id) REFERENCES benchmark_resultauthor;
"""


class Migration(migrations.Migration):
    dependencies = [
        ('benchmark', '0003_auto_20171013_2112'),
    ]

    operations = [
        RunSQL(sql=_sql)
    ]
