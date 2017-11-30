# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0006_auto_20150808_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='notice',
            name='pic_path',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='notice',
            name='url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='notice',
            name='content',
            field=models.TextField(null=True, blank=True),
        ),
    ]
