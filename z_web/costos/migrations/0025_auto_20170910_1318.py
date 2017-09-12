# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20170813_1123'),
        ('parametros', '0005_auto_20160423_1019'),
        ('costos', '0024_auto_20170910_1209'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvanceObra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('avance', models.DecimalField(verbose_name='avance', max_digits=18, decimal_places=3)),
                ('observacion', models.CharField(verbose_name='observación', max_length=255, blank=True, null=True)),
                ('es_proyeccion', models.BooleanField(verbose_name='Es una proyección', default=False)),
                ('centro_costo', models.ForeignKey(verbose_name='centro de costo', null=True, related_name='mis_avances', to='core.Obras')),
                ('periodo', models.ForeignKey(verbose_name='periodo', to='parametros.Periodo')),
            ],
            options={
                'verbose_name': 'avance de obra',
                'verbose_name_plural': 'avances de obra',
                'ordering': ('periodo',),
            },
        ),
        migrations.AlterModelOptions(
            name='costoproyeccion',
            options={'verbose_name': 'proyección de costo', 'verbose_name_plural': 'proyecciones de costo'},
        ),
        migrations.AlterModelOptions(
            name='costoreal',
            options={'verbose_name': 'costo', 'verbose_name_plural': 'costos'},
        ),
        migrations.CreateModel(
            name='AvanceObraProyeccion',
            fields=[
            ],
            options={
                'verbose_name': 'proyección de avance de obra',
                'verbose_name_plural': 'proyecciones de avance de obra',
                'proxy': True,
            },
            bases=('costos.avanceobra',),
        ),
        migrations.CreateModel(
            name='AvanceObraReal',
            fields=[
            ],
            options={
                'verbose_name': 'avance de obra',
                'verbose_name_plural': 'avances de obra',
                'proxy': True,
            },
            bases=('costos.avanceobra',),
        ),
    ]
