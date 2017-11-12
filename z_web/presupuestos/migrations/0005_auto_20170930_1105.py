# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presupuestos', '0004_auto_20170924_0957'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalitempresupuesto',
            name='indirecto',
            field=models.BooleanField(verbose_name='indirecto', default=False),
        ),
        migrations.AddField(
            model_name='itempresupuesto',
            name='indirecto',
            field=models.BooleanField(verbose_name='indirecto', default=False),
        ),
    ]
