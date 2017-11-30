# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_auto_20150808_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='appeal',
            name='pic_path',
            field=models.CharField(max_length=1000, blank=True),
        ),
    ]
