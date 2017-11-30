# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20150827_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tbaccount',
            name='pic_paths',
            field=models.CharField(max_length=600),
        ),
    ]
