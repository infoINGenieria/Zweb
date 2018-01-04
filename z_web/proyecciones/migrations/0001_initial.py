# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20170813_1123'),
        ('parametros', '0006_auto_20171122_2224'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemProyeccionAvanceObra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('avance', models.DecimalField(verbose_name='% de avance', max_digits=18, decimal_places=3)),
                ('periodo', models.ForeignKey(verbose_name='periodo', to='parametros.Periodo')),
            ],
            options={
                'verbose_name': 'ítemes de proyección de avance de obra',
            },
        ),
        migrations.CreateModel(
            name='ProyeccionAvanceObra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('observacion', models.CharField(verbose_name='observación', max_length=255, blank=True, null=True)),
                ('es_base', models.BooleanField(verbose_name='Es linea base', default=False)),
                ('base_numero', models.PositiveSmallIntegerField(verbose_name='Base número', blank=True, null=True)),
                ('centro_costo', models.ForeignKey(verbose_name='centro de costo', related_name='mis_proyecciones_avance', to='core.Obras')),
                ('periodo', models.ForeignKey(verbose_name='periodo de proyección', to='parametros.Periodo')),
            ],
            options={
                'verbose_name': 'proyección de avance de obra',
                'verbose_name_plural': 'proyecciones de avance de obra',
            },
        ),
        migrations.AddField(
            model_name='itemProyeccionAvanceObra',
            name='proyeccion',
            field=models.ForeignKey(verbose_name='proyección', related_name='items', to='proyecciones.ProyeccionAvanceObra'),
        ),
        migrations.AlterUniqueTogether(
            name='ProyeccionAvanceObra',
            unique_together=set([('periodo', 'centro_costo')]),
        ),
    ]
