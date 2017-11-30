# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0022_auto_20151005_1336'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='publish_time',
        ),
    ]
