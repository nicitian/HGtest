# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('others', '0005_tkgoods'),
    ]

    operations = [
        migrations.AddField(
            model_name='tkgoods',
            name='fr',
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='tkgoods',
            name='is_tmall',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tkgoods',
            name='status',
            field=models.SmallIntegerField(default=1),
        ),
    ]
