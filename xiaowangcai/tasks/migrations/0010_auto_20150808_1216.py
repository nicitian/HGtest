# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_auto_20150808_1158'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appeal',
            old_name='type',
            new_name='appealtype',
        ),
    ]
