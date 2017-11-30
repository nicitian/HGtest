# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0023_remove_order_publish_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='publish_time2',
            new_name='publish_time',
        ),
    ]
