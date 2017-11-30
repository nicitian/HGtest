# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0007_auto_20150811_2248'),
    ]

    operations = [
        migrations.RenameField(
            model_name='administrator',
            old_name='loginname',
            new_name='adminname',
        ),
    ]
