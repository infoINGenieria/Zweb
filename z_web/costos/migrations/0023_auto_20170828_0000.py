# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0022_auto_20170827_2358'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='costoparametro',
            options={'verbose_name': 'parametro de costo', 'verbose_name_plural': 'parametros de costos', 'permissions': (('can_view_panel_control', 'Puede ver Panel de Control'), ('can_manage_costos', 'Puede gestionar costos'), ('can_export_panel_control', 'Puede exportar el panel de control'))},
        ),
    ]
