# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_close_sellerreturn',
            field=models.IntegerField(default=0),
        ),
    ]
