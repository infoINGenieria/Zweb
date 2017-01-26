# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20160410_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipos',
            name='nro_serie',
            field=models.CharField(verbose_name='n° serie', blank=True, null=True, max_length=255),
        ),
        migrations.AddField(
            model_name='equipos',
            name='vto_certificacion',
            field=models.DateField(verbose_name='vto certificación', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='equipos',
            name='vto_certificacion_obs',
            field=models.CharField(verbose_name='observación vto. certificación', blank=True, null=True, max_length=255),
        ),
        migrations.AddField(
            model_name='equipos',
            name='vto_ruta',
            field=models.DateField(verbose_name='vto ruta', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='equipos',
            name='año',
            field=models.FloatField(verbose_name='año', db_column='AÑO', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='equipos',
            name='descripcion_vto1',
            field=models.CharField(blank=True, verbose_name='descripción vto1', db_column='DESCRIPCION_VTO1', null=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='equipos',
            name='descripcion_vto2',
            field=models.CharField(blank=True, verbose_name='descripción vto2', db_column='DESCRIPCION_VTO2', null=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='equipos',
            name='descripcion_vto3',
            field=models.CharField(blank=True, verbose_name='descripción vto3', db_column='DESCRIPCION_VTO3', null=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='equipos',
            name='dominio',
            field=models.CharField(blank=True, verbose_name='dominio', db_column='DOMINIO', null=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='equipos',
            name='equipo',
            field=models.CharField(blank=True, verbose_name='tipo de equipo', db_column='EQUIPO', null=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='equipos',
            name='marca',
            field=models.CharField(blank=True, verbose_name='marca', db_column='MARCA', null=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='equipos',
            name='modelo',
            field=models.CharField(blank=True, verbose_name='modelo', db_column='MODELO', null=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='equipos',
            name='n_interno',
            field=models.CharField(blank=True, verbose_name='n° interno', db_column='N_INTERNO', null=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='equipos',
            name='vto_otros1',
            field=models.DateField(verbose_name='fecha vto1', db_column='VTO_OTROS1', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='equipos',
            name='vto_otros2',
            field=models.DateField(verbose_name='fecha vto2', db_column='VTO_OTROS2', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='equipos',
            name='vto_otros3',
            field=models.DateField(verbose_name='fecha vto3', db_column='VTO_OTROS3', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='equipos',
            name='vto_seguro',
            field=models.DateField(verbose_name='vto seguro', db_column='VTO_SEGURO', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='equipos',
            name='vto_vtv',
            field=models.DateField(verbose_name='vto VTV', db_column='VTO_VTV', null=True, blank=True),
        ),
    ]
