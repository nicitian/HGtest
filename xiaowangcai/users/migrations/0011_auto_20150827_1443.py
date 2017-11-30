# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20150814_1930'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['-register_time']},
        ),
        migrations.AlterField(
            model_name='bankcard',
            name='verify_status',
            field=models.SmallIntegerField(default=0, choices=[(0, b'model.verify.need_check'), (2, b'model.verify.check_deny'), (1, b'model.verify.check_pass')]),
        ),
        migrations.AlterField(
            model_name='record',
            name='type',
            field=models.SmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='tbaccount',
            name='status',
            field=models.SmallIntegerField(default=0, choices=[(0, b'model.verify.need_check'), (2, b'model.verify.check_deny'), (1, b'model.verify.check_pass')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='verify_status',
            field=models.SmallIntegerField(default=0, choices=[(0, b'model.verify.need_check'), (2, b'model.verify.check_deny'), (1, b'model.verify.check_pass')]),
        ),
    ]
