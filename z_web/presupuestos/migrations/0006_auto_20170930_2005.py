# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presupuestos', '0005_auto_20170930_1105'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalrevision',
            name='precio_venta_dolar',
            field=models.DecimalField(verbose_name='precio de venta (dolar)', null=True, max_digits=18, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalrevision',
            name='valor_dolar',
            field=models.DecimalField(verbose_name='valor dolar', default=0, max_digits=18, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='revision',
            name='precio_venta_dolar',
            field=models.DecimalField(verbose_name='precio de venta (dolar)', null=True, max_digits=18, decimal_places=2),
        ),
        migrations.AddField(
            model_name='revision',
            name='valor_dolar',
            field=models.DecimalField(verbose_name='valor dolar', default=0, max_digits=18, decimal_places=2),
            preserve_default=False,
        ),
    ]
