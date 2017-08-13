# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0030_auto_20170813_1124'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certificacion',
            name='monto',
        ),
    ]
