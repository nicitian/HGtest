# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0016_auto_20150827_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='update_time',
            field=models.BigIntegerField(null=True, blank=True),
        ),
    ]
