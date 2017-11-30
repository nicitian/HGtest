# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0003_auto_20150805_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notice',
            name='create_time',
            field=models.BigIntegerField(default=1438843792920L),
        ),
    ]
