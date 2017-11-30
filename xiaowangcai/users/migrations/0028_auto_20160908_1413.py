# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0027_auto_20160906_2009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tbaccount',
            name='register_time',
            field=models.IntegerField(null=True),
        ),
    ]
