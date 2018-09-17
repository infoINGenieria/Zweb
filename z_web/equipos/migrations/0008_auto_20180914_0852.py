# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipos', '0007_auto_20180909_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posesionparametros',
            name='precio_del_activo',
            field=models.DecimalField(verbose_name='precio del activo (USD)', max_digits=18, decimal_places=2),
        ),
    ]
