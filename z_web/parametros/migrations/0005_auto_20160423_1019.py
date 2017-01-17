# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parametros', '0004_auto_20151127_1904'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='periodo',
            options={'ordering': ['-fecha_fin'], 'verbose_name': 'periodo', 'verbose_name_plural': 'periodos'},
        ),
    ]
