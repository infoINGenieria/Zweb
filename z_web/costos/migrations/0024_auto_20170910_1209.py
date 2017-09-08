# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0023_costo_es_proyeccion'),
    ]

    operations = [
        migrations.CreateModel(
            name='CostoProyeccion',
            fields=[
            ],
            options={
                'verbose_name': 'Proyección de costo',
                'verbose_name_plural': 'Proyecciones de costo',
                'proxy': True,
            },
            bases=('costos.costo',),
        ),
        migrations.CreateModel(
            name='CostoReal',
            fields=[
            ],
            options={
                'verbose_name': 'Costo',
                'verbose_name_plural': 'Costo',
                'proxy': True,
            },
            bases=('costos.costo',),
        ),
        migrations.AlterModelOptions(
            name='costoparametro',
            options={'verbose_name': 'parametro de costo', 'verbose_name_plural': 'parametros de costos', 'permissions': (('can_view_panel_control', 'Puede ver Panel de Control'), ('can_export_panel_control', 'Puede exportar el panel de control'), ('can_manage_costos', 'Puede gestionar costos'), ('can_generate_reports', 'Puede generar reportes'))},
        ),
    ]
