# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parametros', '0006_auto_20171122_2224'),
        ('equipos', '0004_auto_20180809_2115'),
    ]

    operations = [
        migrations.CreateModel(
            name='TotalFlota',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('monto', models.DecimalField(verbose_name='Total Flota($)', max_digits=18, decimal_places=2)),
                ('valido_desde', models.OneToOneField(verbose_name='válido desde', to='parametros.Periodo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='historicalmanoobravalores',
            name='equipo',
        ),
        migrations.RemoveField(
            model_name='manoobravalores',
            name='equipo',
        ),
        migrations.AddField(
            model_name='costoequipovalores',
            name='costo_equipo_calculado',
            field=models.DecimalField(verbose_name='Costo equipo', default=0, max_digits=18, decimal_places=2),
        ),
        migrations.AddField(
            model_name='costoequipovalores',
            name='costo_mensual_del_activo_calculado',
            field=models.DecimalField(verbose_name='Costo mensual del activo', default=0, max_digits=18, decimal_places=2),
        ),
        migrations.AddField(
            model_name='costoequipovalores',
            name='costo_mensual_del_activo_con_mo_calculado',
            field=models.DecimalField(verbose_name='Costo mensual del activo con Mano de obra', default=0, max_digits=18, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalcostoequipovalores',
            name='costo_equipo_calculado',
            field=models.DecimalField(verbose_name='Costo equipo', default=0, max_digits=18, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalcostoequipovalores',
            name='costo_mensual_del_activo_calculado',
            field=models.DecimalField(verbose_name='Costo mensual del activo', default=0, max_digits=18, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalcostoequipovalores',
            name='costo_mensual_del_activo_con_mo_calculado',
            field=models.DecimalField(verbose_name='Costo mensual del activo con Mano de obra', default=0, max_digits=18, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='manoobravalores',
            name='valido_desde',
            field=models.OneToOneField(verbose_name='válido desde', to='parametros.Periodo'),
        ),
    ]
