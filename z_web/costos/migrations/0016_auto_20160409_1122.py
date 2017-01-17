# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0015_auto_20151228_2221'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='costoparametro',
            options={'verbose_name_plural': 'parametros de costos', 'verbose_name': 'parametro de costo', 'permissions': (('can_view_panel_control', 'Puede ver Panel de Control'), ('can_add_costos_masivo', 'Puede ingresar costos masivos'), ('can_export_panel_control', 'Puede exportar el panel de control'))},
        ),
    ]
