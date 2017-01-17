# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parametros', '0004_auto_20151127_1904'),
        ('costos', '0016_auto_20160409_1122'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchivosAdjuntosPeriodo',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('archivo', models.FileField(verbose_name='archivo', upload_to='adjuntos')),
                ('comentario', models.TextField(verbose_name='comentario', blank=True, null=True)),
                ('periodo', models.ForeignKey(related_name='archivos', to='parametros.Periodo', verbose_name='Periodo')),
            ],
            options={
                'verbose_name': 'archivo adjunto de periodo',
                'verbose_name_plural': 'archivos adjunto de periodos',
            },
        ),
    ]
