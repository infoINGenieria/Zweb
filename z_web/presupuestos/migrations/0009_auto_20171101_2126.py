# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('presupuestos', '0008_auto_20171027_0041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalitempresupuesto',
            name='tipo',
            field=models.ForeignKey(blank=True, null=True, related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to='costos.CostoTipo', db_constraint=False),
        ),
        migrations.AlterField(
            model_name='itempresupuesto',
            name='tipo',
            field=models.ForeignKey(verbose_name='tipo de item', related_name='valores_presupuesto', to='costos.CostoTipo'),
        ),
        migrations.DeleteModel(
            name='TipoItemPresupuesto',
        ),
    ]
