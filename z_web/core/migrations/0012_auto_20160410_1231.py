# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20160106_2130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='obras',
            name='incluir_en_costos',
        ),
        migrations.RemoveField(
            model_name='obras',
            name='prorratea_manoobra',
        ),
        migrations.RemoveField(
            model_name='obras',
            name='prorratea_materiales',
        ),
    ]
