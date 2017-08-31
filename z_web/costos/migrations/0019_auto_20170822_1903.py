# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20170813_1123'),
        ('parametros', '0005_auto_20160423_1019'),
        ('costos', '0018_auto_20170909_1346'),
    ]

    operations = [
        migrations.CreateModel(
            name='Costo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('observacion', models.CharField(verbose_name='observación', max_length=255, blank=True, null=True)),
                ('monto_total', models.DecimalField(verbose_name='$', blank=True, null=True, max_digits=18, decimal_places=2)),
                ('monto_hora', models.DecimalField(verbose_name='$/hs', blank=True, null=True, max_digits=18, decimal_places=2)),
                ('monto_mes', models.DecimalField(verbose_name='$/mes', blank=True, null=True, max_digits=18, decimal_places=2)),
                ('monto_anio', models.DecimalField(verbose_name='$/año', blank=True, null=True, max_digits=18, decimal_places=2)),
                ('centro_costo', models.ForeignKey(verbose_name='centro de costo', null=True, related_name='mis_costos', to='core.Obras')),
                ('familia_equipo', models.ForeignKey(verbose_name='Familia de equipo', null=True, related_name='costos_de_la_familia', to='parametros.FamiliaEquipo')),
                ('periodo', models.ForeignKey(verbose_name='periodo', to='parametros.Periodo')),
            ],
            options={
                'verbose_name': 'costo',
                'verbose_name_plural': 'costos',
                'ordering': ('periodo',),
            },
        ),
        migrations.CreateModel(
            name='CostoTipo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('nombre', models.CharField(verbose_name='nombre', max_length=255)),
                ('codigo', models.CharField(verbose_name='codigo', max_length=8, help_text='Código único para identificar unívocamente el tipo de costo. Máximo largo: 8. Se removerán automáticamente espacios y se convertirá a mayúsculas.')),
                ('relacionado_con', models.CharField(verbose_name='relacionado con', max_length=2, default='cc', choices=[('cc', 'Centro de costos'), ('eq', 'Equipos')], help_text='Especifique si el costo estará asociado a un centro de costos, o asociado a un equipo.')),
                ('unidad_monto', models.CharField(verbose_name='monto expresado en', max_length=8, default='total', choices=[('total', '$'), ('x_hs', '$/hs - $/mes - $/año')], help_text='Especifique si el valor del monto estará expresado en $ (total) o segmentado en $/hs, $/mes o $/año.')),
            ],
            options={
                'verbose_name': 'tipo de costos',
                'verbose_name_plural': 'tipos de costos',
            },
        ),
        migrations.AddField(
            model_name='costo',
            name='tipo_costo',
            field=models.ForeignKey(verbose_name='tipo de costo', to='costos.CostoTipo'),
        ),
    ]
