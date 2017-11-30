# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0030_storerecentbuyeruser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='comment_keyword',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
