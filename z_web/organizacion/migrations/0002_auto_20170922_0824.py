# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizacion', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='unidadnegocio',
            options={'verbose_name': 'unidad de negocio', 'verbose_name_plural': 'unidades de negocio', 'permissions': (('can_manage_presupuestos', 'Puede administrar presupuestos'),)},
        ),
    ]
