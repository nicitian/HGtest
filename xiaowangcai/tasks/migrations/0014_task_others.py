# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0013_auto_20150813_0012'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='others',
            field=models.TextField(null=True, blank=True),
        ),
    ]
