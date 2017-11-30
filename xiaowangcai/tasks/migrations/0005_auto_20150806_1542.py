# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_auto_20150806_1541'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appeal',
            name='pic_path',
        ),
        migrations.RemoveField(
            model_name='appeal',
            name='reason',
        ),
    ]
