# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20180731_2154'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipos',
            name='excluir_costos_taller',
            field=models.BooleanField(verbose_name='excluir de costos de taller', default=False, help_text='Seleccionar si se desea excluir el equipo del cálculo de costos de Taller'),
        ),
    ]
