# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0020_auto_20150905_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='appealtype',
            name='type',
            field=models.SmallIntegerField(default=1),
        ),
    ]