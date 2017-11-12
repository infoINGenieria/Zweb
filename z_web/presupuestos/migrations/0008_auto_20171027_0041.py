# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presupuestos', '0007_auto_20171013_0827'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalrevision',
            name='ganancias',
        ),
        migrations.RemoveField(
            model_name='revision',
            name='ganancias',
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='costo_financiero',
            field=models.DecimalField(verbose_name='costo financiero', null=True, help_text='Sobre Costo industrial', max_digits=18, decimal_places=4),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='imprevistos',
            field=models.DecimalField(verbose_name='imprevistos', null=True, help_text='Sobre costo industrial', max_digits=18, decimal_places=4),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='impuestos_cheque',
            field=models.DecimalField(verbose_name='impuestos al cheque', null=True, help_text='Sobre Venta', max_digits=18, decimal_places=4),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='ingresos_brutos',
            field=models.DecimalField(verbose_name='ingresos brutos', null=True, help_text='Sobre Venta', max_digits=18, decimal_places=4),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='sellado',
            field=models.DecimalField(verbose_name='sellado', null=True, help_text='Sobre Venta', max_digits=18, decimal_places=4),
        ),
        migrations.AlterField(
            model_name='revision',
            name='costo_financiero',
            field=models.DecimalField(verbose_name='costo financiero', null=True, help_text='Sobre Costo industrial', max_digits=18, decimal_places=4),
        ),
        migrations.AlterField(
            model_name='revision',
            name='imprevistos',
            field=models.DecimalField(verbose_name='imprevistos', null=True, help_text='Sobre costo industrial', max_digits=18, decimal_places=4),
        ),
        migrations.AlterField(
            model_name='revision',
            name='impuestos_cheque',
            field=models.DecimalField(verbose_name='impuestos al cheque', null=True, help_text='Sobre Venta', max_digits=18, decimal_places=4),
        ),
        migrations.AlterField(
            model_name='revision',
            name='ingresos_brutos',
            field=models.DecimalField(verbose_name='ingresos brutos', null=True, help_text='Sobre Venta', max_digits=18, decimal_places=4),
        ),
        migrations.AlterField(
            model_name='revision',
            name='sellado',
            field=models.DecimalField(verbose_name='sellado', null=True, help_text='Sobre Venta', max_digits=18, decimal_places=4),
        ),
    ]
