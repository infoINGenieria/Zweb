# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import equipos.models


class Migration(migrations.Migration):

    dependencies = [
        ('equipos', '0005_auto_20180820_0922'),
    ]

    operations = [
        migrations.CreateModel(
            name='LubricanteItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('descripcion', models.CharField(verbose_name='descripción del ítem', max_length=255)),
                ('es_filtro', models.BooleanField(verbose_name='El item es un filtro?', default=True, help_text='Seleccionar para filtros, no seleccionar para lubricantes o fluidos hidráulicos')),
                ('observaciones', models.TextField(verbose_name='observaciones', blank=True, null=True)),
            ],
            options={
                'verbose_name': 'ítem de lubricantes / hidráulicos / filtros',
                'verbose_name_plural': 'ítemes de lubricantes / hidráulicos / filtros',
            },
        ),
        migrations.CreateModel(
            name='LubricantesParametrosItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('cambios_por_anio', models.DecimalField(verbose_name='cambios por año', default=0, max_digits=5, decimal_places=2)),
                ('volumen_por_cambio', models.DecimalField(verbose_name='volumen (L) por cambio', default=1, max_digits=5, decimal_places=2)),
                ('item', models.ForeignKey(related_name='parametros', to='equipos.LubricanteItem')),
            ],
            options={
                'verbose_name': 'ítem de parámetros de lubricantes / hidráulicos /filtros',
                'verbose_name_plural': 'ítemes de parámetros de lubricantes / hidráulicos / filtros',
            },
        ),
        migrations.CreateModel(
            name='LubricantesValoresItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('valor_unitario', models.DecimalField(verbose_name='valor unitario', default=0, help_text='Precio por unidad o litro.', max_digits=18, decimal_places=2)),
                ('costo_por_mes', models.DecimalField(verbose_name='costo ($/m)', max_digits=18, decimal_places=2)),
                ('item', models.ForeignKey(related_name='itemes', to='equipos.LubricanteItem')),
            ],
            options={
                'verbose_name': 'ítem de valores de lubricantes / hidráulicos /filtros',
                'verbose_name_plural': 'ítemes de valores de lubricantes / hidráulicos / filtros',
            },
            bases=(equipos.models.ValoresMixin, models.Model),
        ),
        migrations.AlterModelOptions(
            name='historicallubricantesvalores',
            options={'verbose_name': 'historical valor de lubricantes / hidráulicos / filtros', 'ordering': ('-history_date', '-history_id'), 'get_latest_by': 'history_date'},
        ),
        migrations.AlterModelOptions(
            name='lubricantesvalores',
            options={'verbose_name': 'valor de lubricantes / hidráulicos / filtros', 'verbose_name_plural': 'valores de lubricantes / hidráulicos / filtros'},
        ),
        migrations.RemoveField(
            model_name='historicallubricantesvalores',
            name='precio_filtro_aire',
        ),
        migrations.RemoveField(
            model_name='historicallubricantesvalores',
            name='precio_filtro_combustible',
        ),
        migrations.RemoveField(
            model_name='historicallubricantesvalores',
            name='precio_filtro_hidraulico',
        ),
        migrations.RemoveField(
            model_name='historicallubricantesvalores',
            name='precio_filtro_lubricante',
        ),
        migrations.RemoveField(
            model_name='lubricantesparametros',
            name='cambios_lubricante_en_2000',
        ),
        migrations.RemoveField(
            model_name='lubricantesparametros',
            name='consumo_medio',
        ),
        migrations.RemoveField(
            model_name='lubricantesparametros',
            name='volumen_hidraulico_por_cambio',
        ),
        migrations.RemoveField(
            model_name='lubricantesparametros',
            name='volumen_lubricante_por_cambio',
        ),
        migrations.RemoveField(
            model_name='lubricantesvalores',
            name='precio_filtro_aire',
        ),
        migrations.RemoveField(
            model_name='lubricantesvalores',
            name='precio_filtro_combustible',
        ),
        migrations.RemoveField(
            model_name='lubricantesvalores',
            name='precio_filtro_hidraulico',
        ),
        migrations.RemoveField(
            model_name='lubricantesvalores',
            name='precio_filtro_lubricante',
        ),
        migrations.AddField(
            model_name='lubricantesvaloresitem',
            name='valor',
            field=models.ForeignKey(related_name='valores', to='equipos.LubricantesValores'),
        ),
        migrations.AddField(
            model_name='lubricantesparametrositem',
            name='parametro',
            field=models.ForeignKey(related_name='items_lubricante', to='equipos.LubricantesParametros'),
        ),
    ]
