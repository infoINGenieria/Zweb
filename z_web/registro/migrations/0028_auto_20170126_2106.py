# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0027_auto_20170123_1724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ajustecombustible',
            name='costo_total',
            field=models.FloatField(verbose_name='costo total', blank=True, null=True, help_text='Si ingresa este valor, se ignorará los registros para el periodo y centro de costo asociados'),
        ),
        migrations.AlterField(
            model_name='ajustecombustible',
            name='valor',
            field=models.FloatField(verbose_name='valor de ajuste', blank=True, null=True, help_text='Utilice este valor para ajustar el valor arrojado por el informe'),
        ),
    ]
