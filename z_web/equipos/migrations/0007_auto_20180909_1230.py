# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipos', '0006_auto_20180902_2119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lubricantesvaloresitem',
            name='costo_por_mes',
            field=models.DecimalField(verbose_name='costo ($/m)', blank=True, help_text='No completar, se calculará automáticamente.', max_digits=18, decimal_places=2),
        ),
    ]
