# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_auto_20150807_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='search_entries',
            field=models.CharField(max_length=500),
        ),
    ]
