# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20170812_1333'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userextension',
            options={'verbose_name': 'información adicional', 'verbose_name_plural': 'información adicional'},
        ),
    ]
