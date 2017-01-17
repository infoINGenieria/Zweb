# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0025_auto_20160423_1019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ajustecombustible',
            name='periodo',
            field=models.ForeignKey(related_name='ajustes_combustibles', to='parametros.Periodo'),
        ),
    ]
