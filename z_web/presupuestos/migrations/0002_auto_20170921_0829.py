# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presupuestos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalitempresupuesto',
            name='history_type',
            field=models.CharField(max_length=1, choices=[('+', 'Fecha de creación'), ('~', 'Changed'), ('-', 'Deleted')]),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='aval_por_anticipos',
            field=models.DecimalField(verbose_name='aval por anticipos', null=True, help_text='Sobre porcentaje de la venta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='aval_por_cumplimiento_contrato',
            field=models.DecimalField(verbose_name='aval por cumplimiento de contrato', null=True, help_text='Sobre venta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='aval_por_cumplimiento_garantia',
            field=models.DecimalField(verbose_name='aval por cumplimiento de garantia', null=True, help_text='Sobre venta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='contingencia',
            field=models.DecimalField(verbose_name='contingencia', null=True, help_text='Sobre costos previstos', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='costo_financiero',
            field=models.DecimalField(verbose_name='costo financiero', null=True, help_text='Sobre Costo industrial', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='estructura_no_ree',
            field=models.DecimalField(verbose_name='estructura no contemplada en REE', null=True, help_text='Sobre costos previstos', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='ganancias',
            field=models.DecimalField(verbose_name='ganancias', null=True, help_text='Sobre costo industrial', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='history_type',
            field=models.CharField(max_length=1, choices=[('+', 'Fecha de creación'), ('~', 'Changed'), ('-', 'Deleted')]),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='imprevistos',
            field=models.DecimalField(verbose_name='imprevistos', null=True, help_text='Sobre costo industrial', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='impuestos_cheque',
            field=models.DecimalField(verbose_name='impuestos al cheque', null=True, help_text='Sobre Venta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='impuestos_ganancias',
            field=models.DecimalField(verbose_name='impuestos ganancias', null=True, help_text='Sobre Ganancia Neta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='ingresos_brutos',
            field=models.DecimalField(verbose_name='ingresos brutos', null=True, help_text='Sobre Venta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='precio_venta',
            field=models.DecimalField(verbose_name='precio de venta', null=True, max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='seguro_5',
            field=models.DecimalField(verbose_name='seguro_5', null=True, help_text='Sobre venta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='seguro_caucion',
            field=models.DecimalField(verbose_name='seguro de caución', null=True, help_text='Sobre venta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='historicalrevision',
            name='sellado',
            field=models.DecimalField(verbose_name='sellado', null=True, help_text='Sobre Venta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='revision',
            name='aval_por_anticipos',
            field=models.DecimalField(verbose_name='aval por anticipos', null=True, help_text='Sobre porcentaje de la venta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='revision',
            name='aval_por_cumplimiento_contrato',
            field=models.DecimalField(verbose_name='aval por cumplimiento de contrato', null=True, help_text='Sobre venta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='revision',
            name='aval_por_cumplimiento_garantia',
            field=models.DecimalField(verbose_name='aval por cumplimiento de garantia', null=True, help_text='Sobre venta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='revision',
            name='contingencia',
            field=models.DecimalField(verbose_name='contingencia', null=True, help_text='Sobre costos previstos', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='revision',
            name='costo_financiero',
            field=models.DecimalField(verbose_name='costo financiero', null=True, help_text='Sobre Costo industrial', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='revision',
            name='estructura_no_ree',
            field=models.DecimalField(verbose_name='estructura no contemplada en REE', null=True, help_text='Sobre costos previstos', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='revision',
            name='ganancias',
            field=models.DecimalField(verbose_name='ganancias', null=True, help_text='Sobre costo industrial', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='revision',
            name='imprevistos',
            field=models.DecimalField(verbose_name='imprevistos', null=True, help_text='Sobre costo industrial', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='revision',
            name='impuestos_cheque',
            field=models.DecimalField(verbose_name='impuestos al cheque', null=True, help_text='Sobre Venta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='revision',
            name='impuestos_ganancias',
            field=models.DecimalField(verbose_name='impuestos ganancias', null=True, help_text='Sobre Ganancia Neta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='revision',
            name='ingresos_brutos',
            field=models.DecimalField(verbose_name='ingresos brutos', null=True, help_text='Sobre Venta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='revision',
            name='precio_venta',
            field=models.DecimalField(verbose_name='precio de venta', null=True, max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='revision',
            name='seguro_5',
            field=models.DecimalField(verbose_name='seguro_5', null=True, help_text='Sobre venta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='revision',
            name='seguro_caucion',
            field=models.DecimalField(verbose_name='seguro de caución', null=True, help_text='Sobre venta', max_digits=18, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='revision',
            name='sellado',
            field=models.DecimalField(verbose_name='sellado', null=True, help_text='Sobre Venta', max_digits=18, decimal_places=3),
        ),
    ]
