# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20170813_1123'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalItemPresupuesto',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, db_index=True, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', blank=True, editable=False)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', blank=True, editable=False)),
                ('pesos', models.DecimalField(verbose_name='$', max_digits=18, decimal_places=3)),
                ('dolares', models.DecimalField(verbose_name='USD', max_digits=18, decimal_places=3)),
                ('observaciones', models.TextField(verbose_name='observaciones', blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(null=True, related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical ítem de presupuesto',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalRevision',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, db_index=True, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', blank=True, editable=False)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', blank=True, editable=False)),
                ('version', models.PositiveIntegerField(verbose_name='version')),
                ('fecha', models.DateField(verbose_name='fecha')),
                ('contingencia', models.DecimalField(verbose_name='contingencia', help_text='Sobre costos previstos', max_digits=18, decimal_places=3)),
                ('estructura_no_ree', models.DecimalField(verbose_name='estructura no contemplada en REE', help_text='Sobre costos previstos', max_digits=18, decimal_places=3)),
                ('aval_por_anticipos', models.DecimalField(verbose_name='aval por anticipos', help_text='Sobre porcentaje de la venta', max_digits=18, decimal_places=3)),
                ('seguro_caucion', models.DecimalField(verbose_name='seguro de caución', help_text='Sobre venta', max_digits=18, decimal_places=3)),
                ('aval_por_cumplimiento_contrato', models.DecimalField(verbose_name='aval por cumplimiento de contrato', help_text='Sobre venta', max_digits=18, decimal_places=3)),
                ('aval_por_cumplimiento_garantia', models.DecimalField(verbose_name='aval por cumplimiento de garantia', help_text='Sobre venta', max_digits=18, decimal_places=3)),
                ('seguro_5', models.DecimalField(verbose_name='seguro_5', help_text='Sobre venta', max_digits=18, decimal_places=3)),
                ('imprevistos', models.DecimalField(verbose_name='imprevistos', help_text='Sobre costo industrial', max_digits=18, decimal_places=3)),
                ('ganancias', models.DecimalField(verbose_name='ganancias', help_text='Sobre costo industrial', max_digits=18, decimal_places=3)),
                ('impuestos_ganancias', models.DecimalField(verbose_name='impuestos ganancias', help_text='Sobre Ganancia Neta', max_digits=18, decimal_places=3)),
                ('sellado', models.DecimalField(verbose_name='sellado', help_text='Sobre Venta', max_digits=18, decimal_places=3)),
                ('ingresos_brutos', models.DecimalField(verbose_name='ingresos brutos', help_text='Sobre Venta', max_digits=18, decimal_places=3)),
                ('impuestos_cheque', models.DecimalField(verbose_name='impuestos al cheque', help_text='Sobre Venta', max_digits=18, decimal_places=3)),
                ('costo_financiero', models.DecimalField(verbose_name='costo financiero', help_text='Sobre Costo industrial', max_digits=18, decimal_places=3)),
                ('precio_venta', models.DecimalField(verbose_name='precio de venta', max_digits=18, decimal_places=3)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(null=True, related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical revision',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='ItemPresupuesto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('pesos', models.DecimalField(verbose_name='$', max_digits=18, decimal_places=3)),
                ('dolares', models.DecimalField(verbose_name='USD', max_digits=18, decimal_places=3)),
                ('observaciones', models.TextField(verbose_name='observaciones', blank=True, null=True)),
            ],
            options={
                'verbose_name': 'ítem de presupuesto',
                'verbose_name_plural': 'ítemes de presupuesto',
            },
        ),
        migrations.CreateModel(
            name='Presupuesto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('fecha', models.DateField(verbose_name='fecha')),
                ('aprobado', models.BooleanField(verbose_name='aprobado', default=False)),
                ('centro_costo', models.ForeignKey(verbose_name='centro costo', related_name='presupuestos', to='core.Obras')),
            ],
            options={
                'verbose_name': 'presupuesto',
                'verbose_name_plural': 'presupuestos',
            },
        ),
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('version', models.PositiveIntegerField(verbose_name='version')),
                ('fecha', models.DateField(verbose_name='fecha')),
                ('contingencia', models.DecimalField(verbose_name='contingencia', help_text='Sobre costos previstos', max_digits=18, decimal_places=3)),
                ('estructura_no_ree', models.DecimalField(verbose_name='estructura no contemplada en REE', help_text='Sobre costos previstos', max_digits=18, decimal_places=3)),
                ('aval_por_anticipos', models.DecimalField(verbose_name='aval por anticipos', help_text='Sobre porcentaje de la venta', max_digits=18, decimal_places=3)),
                ('seguro_caucion', models.DecimalField(verbose_name='seguro de caución', help_text='Sobre venta', max_digits=18, decimal_places=3)),
                ('aval_por_cumplimiento_contrato', models.DecimalField(verbose_name='aval por cumplimiento de contrato', help_text='Sobre venta', max_digits=18, decimal_places=3)),
                ('aval_por_cumplimiento_garantia', models.DecimalField(verbose_name='aval por cumplimiento de garantia', help_text='Sobre venta', max_digits=18, decimal_places=3)),
                ('seguro_5', models.DecimalField(verbose_name='seguro_5', help_text='Sobre venta', max_digits=18, decimal_places=3)),
                ('imprevistos', models.DecimalField(verbose_name='imprevistos', help_text='Sobre costo industrial', max_digits=18, decimal_places=3)),
                ('ganancias', models.DecimalField(verbose_name='ganancias', help_text='Sobre costo industrial', max_digits=18, decimal_places=3)),
                ('impuestos_ganancias', models.DecimalField(verbose_name='impuestos ganancias', help_text='Sobre Ganancia Neta', max_digits=18, decimal_places=3)),
                ('sellado', models.DecimalField(verbose_name='sellado', help_text='Sobre Venta', max_digits=18, decimal_places=3)),
                ('ingresos_brutos', models.DecimalField(verbose_name='ingresos brutos', help_text='Sobre Venta', max_digits=18, decimal_places=3)),
                ('impuestos_cheque', models.DecimalField(verbose_name='impuestos al cheque', help_text='Sobre Venta', max_digits=18, decimal_places=3)),
                ('costo_financiero', models.DecimalField(verbose_name='costo financiero', help_text='Sobre Costo industrial', max_digits=18, decimal_places=3)),
                ('precio_venta', models.DecimalField(verbose_name='precio de venta', max_digits=18, decimal_places=3)),
                ('presupuesto', models.ForeignKey(verbose_name='presupuesto', related_name='revisiones', to='presupuestos.Presupuesto')),
            ],
            options={
                'verbose_name': 'revision',
                'verbose_name_plural': 'revisiones',
            },
        ),
        migrations.CreateModel(
            name='TipoItemPresupuesto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación', auto_now_add=True)),
                ('modified_at', models.DateTimeField(verbose_name='Fecha de modificación', auto_now=True)),
                ('nombre', models.CharField(verbose_name='nombre', max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'tipo de ítem de presupuesto',
                'verbose_name_plural': 'tipos de ítem de presupuesto',
            },
        ),
        migrations.AddField(
            model_name='itempresupuesto',
            name='revision',
            field=models.ForeignKey(verbose_name='revision', related_name='items', to='presupuestos.Revision'),
        ),
        migrations.AddField(
            model_name='itempresupuesto',
            name='tipo',
            field=models.ForeignKey(verbose_name='tipo de item', related_name='valores', to='presupuestos.TipoItemPresupuesto'),
        ),
        migrations.AddField(
            model_name='historicalrevision',
            name='presupuesto',
            field=models.ForeignKey(blank=True, null=True, related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to='presupuestos.Presupuesto', db_constraint=False),
        ),
        migrations.AddField(
            model_name='historicalitempresupuesto',
            name='revision',
            field=models.ForeignKey(blank=True, null=True, related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to='presupuestos.Revision', db_constraint=False),
        ),
        migrations.AddField(
            model_name='historicalitempresupuesto',
            name='tipo',
            field=models.ForeignKey(blank=True, null=True, related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, to='presupuestos.TipoItemPresupuesto', db_constraint=False),
        ),
    ]
