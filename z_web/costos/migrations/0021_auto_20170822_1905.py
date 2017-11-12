# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrar_todos_los_costos(apps, schema_editor):
    """
    Migración de todos los costas al nuevo esquema de costos.
    """
    Costo = apps.get_model('costos.Costo')
    CostoTipo = apps.get_model('costos.CostoTipo')

    # por cc
    CostoManoObra = apps.get_model('costos.CostoManoObra')
    CostoSubContrato = apps.get_model('costos.CostoSubContrato')
    MaterialesTotal = apps.get_model('costos.MaterialesTotal')

    # por equipos
    LubricanteFluidosHidro = apps.get_model('costos.LubricanteFluidosHidro')
    TrenRodaje = apps.get_model('costos.TrenRodaje')
    ReservaReparaciones = apps.get_model('costos.ReserveReparaciones')
    CostoPosesion = apps.get_model('costos.CostoPosesion')

    # mano de obra
    mano_obra = CostoTipo.objects.get(codigo='MANOOBRA')
    for item in CostoManoObra.objects.all():
        Costo.objects.create(
            tipo_costo=mano_obra, periodo=item.periodo,
            centro_costo=item.obra, monto_total="%s" % item.monto)

    # subcontratos
    subcontratos = CostoTipo.objects.get(codigo='SUBCONTR')
    for item in CostoSubContrato.objects.all():
        Costo.objects.create(
            tipo_costo=subcontratos, periodo=item.periodo,
            centro_costo=item.obra, monto_total="%s" % item.monto)

    # Materiales
    materiales = CostoTipo.objects.get(codigo='MATERIAL')
    for item in MaterialesTotal.objects.all():
        Costo.objects.create(
            tipo_costo=materiales, periodo=item.periodo,
            centro_costo=item.obra, monto_total="%s" % item.monto)

    # lubricantes
    lubricantes = CostoTipo.objects.get(codigo='LUBR_FLU')
    for item in LubricanteFluidosHidro.objects.all():
        Costo.objects.create(
            tipo_costo=lubricantes, periodo=item.periodo, familia_equipo=item.familia_equipo,
            monto_hora="%s" % item.monto_hora, monto_mes="%s" % item.monto_mes)

    # tren de rodaje
    tren = CostoTipo.objects.get(codigo='TRENRODA')
    for item in TrenRodaje.objects.all():
        Costo.objects.create(
            tipo_costo=tren, periodo=item.periodo, familia_equipo=item.familia_equipo,
            monto_hora="%s" % item.monto_hora, monto_mes="%s" % item.monto_mes)

    # reparaciones
    reparaciones = CostoTipo.objects.get(codigo='R_REPARA')
    for item in ReservaReparaciones.objects.all():
        Costo.objects.create(
            tipo_costo=reparaciones, periodo=item.periodo, familia_equipo=item.familia_equipo,
            monto_hora="%s" % item.monto_hora, monto_mes="%s" % item.monto_mes)

    # posesion
    posesion = CostoTipo.objects.get(codigo='POSESION')
    for item in CostoPosesion.objects.all():
        Costo.objects.create(
            tipo_costo=posesion, periodo=item.periodo, familia_equipo=item.familia_equipo,
            monto_hora="%s" % item.monto_hora, monto_mes="%s" % item.monto_mes,
            monto_anio="%s" % item.monto_año)

    total = CostoManoObra.objects.count() + CostoSubContrato.objects.count() + \
            MaterialesTotal.objects.count() + LubricanteFluidosHidro.objects.count() + \
            TrenRodaje.objects.count() + ReservaReparaciones.objects.count() + \
            CostoPosesion.objects.count()

    if total != Costo.objects.count():
        raise Exception("Los totales no coinciden")


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0020_auto_20170822_1903'),
    ]

    operations = [
        migrations.RunPython(migrar_todos_los_costos, migrations.RunPython.noop)
    ]
