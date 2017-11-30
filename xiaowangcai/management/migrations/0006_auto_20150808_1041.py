# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0005_auto_20150808_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recharge',
            name='verify_status',
            field=models.SmallIntegerField(default=0, choices=[(1, b'model.verify.check_pass'), (2, b'model.verify.check_deny'), (0, b'model.verify.need_check')]),
        ),
        migrations.AlterField(
            model_name='withdraw',
            name='verify_status',
            field=models.SmallIntegerField(default=0, choices=[(1, b'model.verify.check_pass'), (2, b'model.verify.check_deny'), (0, b'model.verify.need_check')]),
        ),
    ]
