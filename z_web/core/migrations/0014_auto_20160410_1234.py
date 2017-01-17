# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20160410_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='obras',
            name='prorratea_costos',
            field=models.BooleanField(default=False, help_text='Si está seleccionada, los costos se prorratean en los demás CC', verbose_name='¿Prorratea Costos?'),
        ),
    ]
