# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def crear_tipo_costos(apps, schema_editor):
    CostoTipo = apps.get_model('costos.CostoTipo')
    # Relacionado con CC
    CostoTipo.objects.create(nombre='Mano de obra', codigo='MANOOBRA')
    CostoTipo.objects.create(nombre='Subcontratos', codigo="SUBCONTR")
    CostoTipo.objects.create(nombre='Materiales', codigo="MATERIAL")

    # Relacionado con equipos
    CostoTipo.objects.create(
        nombre='Lubricantes y fluidos hidráulicos', codigo='LUBR_FLU',
        relacionado_con='eq', unidad_monto='x_hs'
    )
    CostoTipo.objects.create(
        nombre='Tren de rodaje', codigo='TRENRODA',
        relacionado_con='eq', unidad_monto='x_hs'
    )
    CostoTipo.objects.create(
        nombre='Reserva de reparaciones', codigo='R_REPARA',
        relacionado_con='eq', unidad_monto='x_hs'
    )
    CostoTipo.objects.create(
        nombre='Posesión', codigo='POSESION',
        relacionado_con='eq', unidad_monto='x_hs'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0019_auto_20170822_1903'),
    ]

    operations = [
        migrations.RunPython(crear_tipo_costos, migrations.RunPython.noop)
    ]
