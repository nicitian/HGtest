# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_remove_user_notice'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='notice',
            field=models.IntegerField(default=0),
        ),
    ]
