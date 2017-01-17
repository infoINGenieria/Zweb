# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parametros', '0004_auto_20151127_1904'),
        ('registro', '0020_auto_20151230_1924'),
    ]

    operations = [
        migrations.CreateModel(
            name='AjusteCombustible',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('valor', models.FloatField(verbose_name='valor de ajuste')),
                ('comentarios', models.TextField(null=True, verbose_name='comentarios', blank=True)),
                ('periodo', models.ForeignKey(to='parametros.Periodo', related_name='ajustes_combustibles')),
            ],
            options={
                'verbose_name': 'ajuste de combustible',
                'verbose_name_plural': 'ajustes de combustible',
            },
        ),
    ]
