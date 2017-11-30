# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('others', '0007_tkgoods_create_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tkgoods',
            name='quan_link',
            field=models.TextField(),
        ),
    ]
