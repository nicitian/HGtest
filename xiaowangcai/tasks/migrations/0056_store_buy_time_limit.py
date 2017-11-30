# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0055_auto_20160116_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='buy_time_limit',
            field=models.BigIntegerField(default=30),
        ),
    ]
