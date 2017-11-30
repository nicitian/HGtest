# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DailyReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.SmallIntegerField()),
                ('date', models.DateField()),
                ('value', models.IntegerField(null=True, blank=True)),
                ('amount', models.DecimalField(null=True, max_digits=11, decimal_places=2, blank=True)),
            ],
        ),
    ]
