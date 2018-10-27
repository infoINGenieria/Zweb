# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizacion', '0002_auto_20170922_0824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unidadnegocio',
            name='observaciones',
            field=models.TextField(blank=True),
        ),
    ]
