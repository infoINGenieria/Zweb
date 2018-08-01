# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipos', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='costoequipovalores',
            options={'verbose_name': 'valor de costo equipo', 'verbose_name_plural': 'valores de costo de equipo'},
        ),
        migrations.AlterModelOptions(
            name='equipoalquiladovalores',
            options={'verbose_name': 'valor de equipo alquilado', 'verbose_name_plural': 'valores de equipos alquilados'},
        ),
        migrations.AlterModelOptions(
            name='lubricantesparametros',
            options={'verbose_name': 'parámetro de lubricante', 'verbose_name_plural': 'parámetros de lubricantes'},
        ),
        migrations.AlterModelOptions(
            name='lubricantesvalores',
            options={'verbose_name': 'valor de lubricante', 'verbose_name_plural': 'valores de lubricantes'},
        ),
        migrations.AlterModelOptions(
            name='posesionparametros',
            options={'verbose_name': 'parámetro de posesión', 'verbose_name_plural': 'parámetros de posesion'},
        ),
        migrations.AlterModelOptions(
            name='posesionvalores',
            options={'verbose_name': 'valor de posesión', 'verbose_name_plural': 'valores de posesión'},
        ),
        migrations.AlterModelOptions(
            name='reparacionesparametros',
            options={'verbose_name': 'parámetro de reparación', 'verbose_name_plural': 'parámetros de reparaciones'},
        ),
        migrations.AlterModelOptions(
            name='reparacionesvalores',
            options={'verbose_name': 'valor de reparación', 'verbose_name_plural': 'valores de reparaciones'},
        ),
        migrations.AlterModelOptions(
            name='trenrodajeparametros',
            options={'verbose_name': 'parámetro de tren de rodaje', 'verbose_name_plural': 'parámetros de tren de rodaje'},
        ),
        migrations.AlterModelOptions(
            name='trenrodajevalores',
            options={'verbose_name': 'valor de tren de rodaje', 'verbose_name_plural': 'valores de tren de rodaje'},
        ),
    ]
