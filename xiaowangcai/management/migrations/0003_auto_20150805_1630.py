# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0002_auto_20150805_0829'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notice',
            options={'ordering': ['-create_time']},
        ),
        migrations.AddField(
            model_name='notice',
            name='title',
            field=models.CharField(default='', max_length=60),
            preserve_default=False,
        ),
    ]
