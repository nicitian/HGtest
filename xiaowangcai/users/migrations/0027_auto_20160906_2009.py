# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_tag'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='user',
        ),
        migrations.AddField(
            model_name='tbaccount',
            name='age',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tbaccount',
            name='gender',
            field=models.SmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tbaccount',
            name='is_credit_card_open',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tbaccount',
            name='is_huabei_open',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tbaccount',
            name='register_time',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tbaccount',
            name='wangwang_level',
            field=models.SmallIntegerField(null=True, choices=[(1, b'tb.level.sanxing'), (2, b'tb.level.siwuxing'), (3, b'tb.level.yizuan'), (4, b'tb.level.erzuan'), (5, b'tb.level.sanzuan'), (6, b'tb.level.sizuan')]),
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
    ]
