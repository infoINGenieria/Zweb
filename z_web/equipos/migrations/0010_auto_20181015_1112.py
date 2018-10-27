# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipos', '0009_auto_20180916_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trenrodajeparametros',
            name='abracion',
            field=models.DecimalField(verbose_name='abración', blank=True, null=True, max_digits=5, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='trenrodajeparametros',
            name='cantidad_neumaticos',
            field=models.IntegerField(verbose_name='neumáticos por equipo', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trenrodajeparametros',
            name='factor_basico',
            field=models.DecimalField(verbose_name='factor básico', blank=True, null=True, max_digits=5, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='trenrodajeparametros',
            name='impacto',
            field=models.DecimalField(verbose_name='impacto', blank=True, null=True, max_digits=5, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='trenrodajeparametros',
            name='medidas',
            field=models.CharField(verbose_name='medidas', max_length=24, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trenrodajeparametros',
            name='vida_util_neumatico',
            field=models.IntegerField(verbose_name='vida util estimada (h)', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trenrodajeparametros',
            name='z',
            field=models.DecimalField(verbose_name='z', blank=True, null=True, max_digits=5, decimal_places=2),
        ),
    ]
