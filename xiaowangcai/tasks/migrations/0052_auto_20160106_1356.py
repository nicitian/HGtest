# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0051_auto_20160103_1605'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appeal',
            options={'ordering': ['-create_time']},
        ),
    ]
