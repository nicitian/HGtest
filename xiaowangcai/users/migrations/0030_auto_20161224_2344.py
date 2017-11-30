# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0029_auto_20161023_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='haoping_order_num',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='is_new',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='user',
            name='liulan_order_num',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='order_money_limit',
            field=models.IntegerField(null=True),
        ),
    ]
