# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presupuestos', '0006_auto_20170930_2005'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalrevision',
            name='precio_venta',
        ),
        migrations.RemoveField(
            model_name='historicalrevision',
            name='precio_venta_dolar',
        ),
        migrations.RemoveField(
            model_name='revision',
            name='precio_venta',
        ),
        migrations.RemoveField(
            model_name='revision',
            name='precio_venta_dolar',
        ),
        migrations.AddField(
            model_name='historicalrevision',
            name='ordenes_cambio',
            field=models.DecimalField(verbose_name='órdenes de cambio', null=True, max_digits=18, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalrevision',
            name='reajustes_precio',
            field=models.DecimalField(verbose_name='reajustes de precio', null=True, max_digits=18, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalrevision',
            name='reclamos_reconocidos',
            field=models.DecimalField(verbose_name='reclamos reconocidos', null=True, max_digits=18, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalrevision',
            name='venta_contractual_b0',
            field=models.DecimalField(verbose_name='venta contractual base cero', null=True, max_digits=18, decimal_places=2),
        ),
        migrations.AddField(
            model_name='revision',
            name='ordenes_cambio',
            field=models.DecimalField(verbose_name='órdenes de cambio', null=True, max_digits=18, decimal_places=2),
        ),
        migrations.AddField(
            model_name='revision',
            name='reajustes_precio',
            field=models.DecimalField(verbose_name='reajustes de precio', null=True, max_digits=18, decimal_places=2),
        ),
        migrations.AddField(
            model_name='revision',
            name='reclamos_reconocidos',
            field=models.DecimalField(verbose_name='reclamos reconocidos', null=True, max_digits=18, decimal_places=2),
        ),
        migrations.AddField(
            model_name='revision',
            name='venta_contractual_b0',
            field=models.DecimalField(verbose_name='venta contractual base cero', null=True, max_digits=18, decimal_places=2),
        ),
    ]
