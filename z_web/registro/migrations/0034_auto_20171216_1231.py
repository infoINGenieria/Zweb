# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0033_auto_20171016_2221'),
    ]

    operations = [
        migrations.RenameField(
            model_name='certificacionitem',
            old_name='descripcion',
            new_name='observaciones'
        ),
        migrations.AddField(
            model_name='certificacionitem',
            name='concepto',
            field=models.CharField(verbose_name='concepto', max_length=16, default='basica', choices=[('basica', 'Básica'), ('cambios', 'Órdenes de cambio'), ('reajuste', 'Reajuste de precios'), ('reclamos', 'Reclamos reconocidos')]),
        )
    ]
