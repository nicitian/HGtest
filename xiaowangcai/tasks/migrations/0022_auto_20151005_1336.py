# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0021_appealtype_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='publish_time2',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='search_entries',
            field=models.CharField(max_length=1000),
        ),
    ]
