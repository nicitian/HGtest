# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('others', '0003_auto_20150902_2313'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dailyreport',
            options={'ordering': ['-date']},
        ),
    ]
