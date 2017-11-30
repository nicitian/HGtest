# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0024_auto_20151006_0124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='device',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(2, b'model.device.ios'), (1, b'model.device.android'), (3, b'model.device.pc'), (0, b'model.device.unknown')]),
        ),
    ]
