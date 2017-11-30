# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20151109_0137'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='notice',
            field=models.IntegerField(default=0),
        ),
    ]
