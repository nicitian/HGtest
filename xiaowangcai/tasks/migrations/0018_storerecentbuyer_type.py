# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0017_order_update_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='storerecentbuyer',
            name='type',
            field=models.SmallIntegerField(default=1),
            preserve_default=False,
        ),
    ]
