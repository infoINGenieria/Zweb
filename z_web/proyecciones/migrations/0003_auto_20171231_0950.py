# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parametros', '0006_auto_20171122_2224'),
        ('core', '0019_auto_20170813_1123'),
        ('proyecciones', '0002_auto_20171223_1020'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemProyeccionCertificacion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('monto', models.DecimalField(verbose_name='Monto ($)', max_digits=18, decimal_places=2)),
                ('periodo', models.ForeignKey(verbose_name='periodo', to='parametros.Periodo')),
            ],
            options={
                'verbose_name': 'ítemes de proyección de certificación',
                'ordering': ('periodo__fecha_fin',),
            },
        ),
        migrations.CreateModel(
            name='ProyeccionCertificacion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('observacion', models.CharField(verbose_name='observación', max_length=255, blank=True, null=True)),
                ('centro_costo', models.ForeignKey(verbose_name='centro de costo', related_name='mis_proyecciones_certificacion', to='core.Obras')),
                ('periodo', models.ForeignKey(verbose_name='periodo de proyección', to='parametros.Periodo')),
            ],
            options={
                'verbose_name': 'proyeccion de certificación',
                'verbose_name_plural': 'proyecciones de certificación',
            },
        ),
        migrations.AlterModelOptions(
            name='itemproyeccionavanceobra',
            options={'verbose_name': 'ítemes de proyección de avance de obra', 'ordering': ('periodo__fecha_fin',)},
        ),
        migrations.AddField(
            model_name='itemproyeccioncertificacion',
            name='proyeccion',
            field=models.ForeignKey(verbose_name='proyección', related_name='items', to='proyecciones.ProyeccionCertificacion'),
        ),
        migrations.AlterUniqueTogether(
            name='proyeccioncertificacion',
            unique_together=set([('periodo', 'centro_costo')]),
        ),
        migrations.AddField(
            model_name='proyeccioncertificacion',
            name='base_numero',
            field=models.PositiveSmallIntegerField(verbose_name='Base número', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='proyeccioncertificacion',
            name='es_base',
            field=models.BooleanField(verbose_name='Es linea base', default=False),
        ),
    ]
