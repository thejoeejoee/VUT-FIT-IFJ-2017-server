# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-21 21:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0005_auto_20171121_2206'),
    ]

    operations = [
        migrations.CreateModel(
            name='VBenchmarkResultPriceProgress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateField()),
            ],
            options={
                'managed': False,
                'db_table': 'v_benchmark_result_price_progress',
            },
        ),
        migrations.AlterModelOptions(
            name='resultauthor',
            options={'ordering': ['x_created']},
        ),
        migrations.AlterModelOptions(
            name='team',
            options={'ordering': ['x_created']},
        ),
        migrations.AlterModelOptions(
            name='testcase',
            options={'ordering': ('section', 'name')},
        ),
        migrations.AlterField(
            model_name='testcase',
            name='info',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
