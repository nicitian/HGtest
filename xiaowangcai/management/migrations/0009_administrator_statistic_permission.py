# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0008_auto_20150815_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='administrator',
            name='statistic_permission',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
