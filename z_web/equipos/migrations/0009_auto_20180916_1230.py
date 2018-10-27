# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipos', '0008_auto_20180914_0852'),
    ]

    operations = [
        migrations.AddField(
            model_name='totalflota',
            name='cantidad',
            field=models.IntegerField(verbose_name='Cantidad equipos', default=0),
        ),
        migrations.AlterField(
            model_name='totalflota',
            name='monto',
            field=models.DecimalField(verbose_name='Total Flota($)', default=0, max_digits=18, decimal_places=2),
        ),
    ]
