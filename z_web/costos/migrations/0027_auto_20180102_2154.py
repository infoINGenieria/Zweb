# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0026_auto_20170912_0048'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AvanceObraProyeccion',
        ),
        migrations.DeleteModel(
            name='AvanceObraReal',
        ),
    ]
