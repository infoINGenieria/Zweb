# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parametros', '0006_auto_20171122_2224'),
        ('core', '0022_auto_20180701_1157'),
    ]

    operations = [
        migrations.CreateModel(
            name='CostoEquipoValores',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('markup', models.DecimalField(verbose_name='Mark Up (%)', max_digits=18, decimal_places=2)),
                ('equipo', models.ForeignKey(verbose_name='equipo', to='core.Equipos')),
                ('valido_desde', models.ForeignKey(verbose_name='válido desde', to='parametros.Periodo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EquipoAlquiladoValores',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('alquiler', models.DecimalField(verbose_name='Desgastables + mano de obra + etc', max_digits=18, decimal_places=2)),
                ('equipo', models.ForeignKey(verbose_name='equipo', to='core.Equipos')),
                ('valido_desde', models.ForeignKey(verbose_name='válido desde', to='parametros.Periodo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LubricantesParametros',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('hp', models.DecimalField(verbose_name='HP', null=True, max_digits=18, decimal_places=2)),
                ('consumo_medio', models.DecimalField(verbose_name='consumo medio (l/h)', null=True, max_digits=18, decimal_places=3)),
                ('cambios_lubricante_en_2000', models.DecimalField(verbose_name='cambios de lubricante en 2000h', null=True, max_digits=5, decimal_places=2)),
                ('volumen_lubricante_por_cambio', models.DecimalField(verbose_name='volumen (L) de lubricante por cambio', null=True, max_digits=5, decimal_places=2)),
                ('volumen_hidraulico_por_cambio', models.DecimalField(verbose_name='volumen (L) hidráulico por cambio', null=True, max_digits=5, decimal_places=2)),
                ('equipo', models.ForeignKey(verbose_name='equipo', to='core.Equipos')),
                ('valido_desde', models.ForeignKey(verbose_name='válido desde', to='parametros.Periodo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LubricantesValores',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('precio_filtro_aire', models.DecimalField(verbose_name='CU Filtro Aire', max_digits=18, decimal_places=3)),
                ('precio_filtro_combustible', models.DecimalField(verbose_name='CU Filtro Combustible', max_digits=18, decimal_places=3)),
                ('precio_filtro_hidraulico', models.DecimalField(verbose_name='CU Filtro Hidráulico', max_digits=18, decimal_places=3)),
                ('precio_filtro_lubricante', models.DecimalField(verbose_name='CU Filtro Lubricante', max_digits=18, decimal_places=3)),
                ('equipo', models.ForeignKey(verbose_name='equipo', to='core.Equipos')),
                ('valido_desde', models.ForeignKey(verbose_name='válido desde', to='parametros.Periodo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ManoObraValores',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('taller', models.DecimalField(verbose_name='taller', max_digits=18, decimal_places=2)),
                ('plataforma_combustible', models.DecimalField(verbose_name='plataforma de combustible', max_digits=18, decimal_places=2)),
                ('carretones', models.DecimalField(verbose_name='carretones', max_digits=18, decimal_places=2)),
                ('equipo', models.ForeignKey(verbose_name='equipo', to='core.Equipos')),
                ('valido_desde', models.ForeignKey(verbose_name='válido desde', to='parametros.Periodo')),
            ],
            options={
                'verbose_name': 'valor de mano de obra',
                'verbose_name_plural': 'valores de mano de obra',
            },
        ),
        migrations.CreateModel(
            name='ParametrosGenerales',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('consumo_equipo_viales', models.DecimalField(verbose_name='consumo específico equipos viales (l/h/HP)', max_digits=5, decimal_places=3)),
                ('consumo_equipo_automotor', models.DecimalField(verbose_name='consumo específico equipos automotor (l/h/HP)', max_digits=5, decimal_places=3)),
                ('precio_gasoil', models.DecimalField(verbose_name='precio GO ($/l a granel sin impuestos deducibles)', max_digits=18, decimal_places=3)),
                ('precio_lubricante', models.DecimalField(verbose_name='precio lubricante $/l (a granel sin impuestos deducibles)', max_digits=18, decimal_places=3)),
                ('precio_hidraulico', models.DecimalField(verbose_name='precio fluido hidráulico (a granel sin impuestos deducibles)', max_digits=18, decimal_places=3)),
                ('horas_por_dia', models.IntegerField(verbose_name='horas por día', default=6)),
                ('dias_por_mes', models.IntegerField(verbose_name='días por mes', default=21)),
                ('horas_trabajo_anio', models.IntegerField(verbose_name='horas trabajo por año', default=1584)),
                ('valor_dolar', models.DecimalField(verbose_name='USD/$', max_digits=18, decimal_places=3)),
                ('valido_desde', models.OneToOneField(verbose_name='válido desde', to='parametros.Periodo')),
            ],
            options={
                'verbose_name': 'parámetro general de taller',
                'verbose_name_plural': 'parámetros generales de taller',
            },
        ),
        migrations.CreateModel(
            name='PosesionParametros',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('posesion_hs', models.IntegerField(verbose_name='periodo de posesion (h)')),
                ('precio_del_activo', models.IntegerField(verbose_name='precio del activo (USD)')),
                ('residual', models.DecimalField(verbose_name='residual', max_digits=5, decimal_places=2)),
                ('equipo', models.ForeignKey(verbose_name='equipo', to='core.Equipos')),
                ('valido_desde', models.ForeignKey(verbose_name='válido desde', to='parametros.Periodo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PosesionValores',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('seguros', models.DecimalField(verbose_name='seguros', help_text='$/mes', max_digits=18, decimal_places=2)),
                ('ruta', models.DecimalField(verbose_name='R.U.T.A', help_text='$/mes', max_digits=18, decimal_places=2)),
                ('vtv', models.DecimalField(verbose_name='VTV', help_text='$/mes', max_digits=18, decimal_places=2)),
                ('certificacion', models.DecimalField(verbose_name='certificacion (IRAM)', help_text='$/mes', max_digits=18, decimal_places=2)),
                ('habilitaciones', models.DecimalField(verbose_name='habilitaciones', help_text='$/mes', max_digits=18, decimal_places=2)),
                ('rsv', models.DecimalField(verbose_name='RSV', help_text='$/mes', max_digits=18, decimal_places=2)),
                ('vhf', models.DecimalField(verbose_name='VHF', help_text='$/mes', max_digits=18, decimal_places=2)),
                ('impuestos', models.DecimalField(verbose_name='impuestos', help_text='$/mes', max_digits=18, decimal_places=2)),
                ('equipo', models.ForeignKey(verbose_name='equipo', to='core.Equipos')),
                ('valido_desde', models.ForeignKey(verbose_name='válido desde', to='parametros.Periodo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReparacionesParametros',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('factor_basico', models.DecimalField(verbose_name='factor básico de reparación', max_digits=18, decimal_places=2)),
                ('multiplicador', models.DecimalField(verbose_name='multiplicador de duración prolongada', max_digits=18, decimal_places=2)),
                ('equipo', models.ForeignKey(verbose_name='equipo', to='core.Equipos')),
                ('valido_desde', models.ForeignKey(verbose_name='válido desde', to='parametros.Periodo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReparacionesValores',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('equipo', models.ForeignKey(verbose_name='equipo', to='core.Equipos')),
                ('valido_desde', models.ForeignKey(verbose_name='válido desde', to='parametros.Periodo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TrenRodajeParametros',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('vida_util_neumatico', models.IntegerField(verbose_name='vida util estimada (h)', null=True)),
                ('cantidad_neumaticos', models.IntegerField(verbose_name='neumáticos por equipo', null=True)),
                ('medidas', models.CharField(verbose_name='medidas', max_length=24, null=True)),
                ('factor_basico', models.DecimalField(verbose_name='factor básico', null=True, max_digits=5, decimal_places=2)),
                ('impacto', models.DecimalField(verbose_name='impacto', null=True, max_digits=5, decimal_places=2)),
                ('abracion', models.DecimalField(verbose_name='abración', null=True, max_digits=5, decimal_places=2)),
                ('z', models.DecimalField(verbose_name='z', null=True, max_digits=5, decimal_places=2)),
                ('equipo', models.ForeignKey(verbose_name='equipo', to='core.Equipos')),
                ('valido_desde', models.ForeignKey(verbose_name='válido desde', to='parametros.Periodo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TrenRodajeValores',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('precio_neumatico', models.DecimalField(verbose_name='CU Neumático', max_digits=18, decimal_places=3)),
                ('equipo', models.ForeignKey(verbose_name='equipo', to='core.Equipos')),
                ('valido_desde', models.ForeignKey(verbose_name='válido desde', to='parametros.Periodo')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
