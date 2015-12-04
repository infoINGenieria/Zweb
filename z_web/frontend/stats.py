from collections import defaultdict

from django.db.models import Count, When, Case, Sum

from costos.models import (LubricanteFluidosHidro, TrenRodaje, CostoPosesion, ReserveReparaciones, CostoParametro,
                           CostoManoObra, CostoSubContrato, MaterialesTotal)
from core.models import Obras
from registro.models import Partediario
from zweb_utils.format import decimal_format


def get_calculo_costo(costos, valores, horas_dia, total=0):
    val = costos.get(valores["equipo__equipo__familia_equipo_id"], 0) * horas_dia * valores["dias_mes"]
    total += val
    return total, decimal_format(val)


def calcular_item_costo(report, nombre_tipo, datos, no_prorrat, prorrat=[], multiplicador=1):
    lista = [nombre_tipo, ]

    for x in no_prorrat:
        lista.append(datos.get(x, 0) * multiplicador if datos.get(x, 0) else 0)
    report.append(lista)

    if prorrat:
        lista_prorrat = ["Prorrateo {}".format(nombre_tipo), ]
        total_prorrateo = 0
        for x in prorrat:
            data = datos.get(x, 0)
            if data:
                total_prorrateo += (data * multiplicador)
        total_prorrateo = total_prorrateo / len(no_prorrat)
        for x in no_prorrat:
            lista_prorrat.append(total_prorrateo)
        report.append(lista_prorrat)
    return report



def get_utlizacion_equipo(periodo):
    qs = Partediario.objects.filter(
        fecha__lte=periodo.fecha_fin, fecha__gte=periodo.fecha_inicio, situacion__id=1).exclude(
        equipo__equipo_id=1).exclude(equipo_id__isnull=True).values(
        'equipo__equipo_id', 'equipo__equipo__n_interno', 'funcion__funcion', 'operario__nombre',
        'obra__obra', 'obra_id', 'equipo__equipo__familia_equipo_id').annotate(dias_mes=Count('id')).order_by(
        'obra_id', '-equipo__equipo__n_interno')

    processed = defaultdict(list)
    for result in qs:
        processed[result["obra__obra"]].append(result)
    result = dict(processed.items())
    ids = list(set(x["equipo__equipo__familia_equipo_id"] for x in qs))
    param = CostoParametro.vigentes.get_vigente_el_periodo(periodo).first()
    # calculo de lubricantes
    lubris = dict(LubricanteFluidosHidro.objects.filter(
        periodo=periodo, familia_equipo_id__in=ids).values_list('familia_equipo', 'monto_hora'))
    # calculo de tren
    tren = dict(TrenRodaje.objects.filter(periodo=periodo, familia_equipo_id__in=ids).values_list('familia_equipo', 'monto_hora'))
    # calculo de posesion
    posesion = dict(CostoPosesion.objects.filter(periodo=periodo, familia_equipo_id__in=ids).values_list('familia_equipo', 'monto_hora'))
    # calculo de reparacion
    repara = dict(ReserveReparaciones.objects.filter(periodo=periodo, familia_equipo_id__in=ids).values_list('familia_equipo', 'monto_hora'))
    totales = dict()
    for k, v in result.items():
        total = 0
        for l in v:
            total, l["fluido"] = get_calculo_costo(lubris, l, param.dias_mes, total)  # lubris.get(l["equipo__equipo__familia_equipo_id"], 0) * param.horas_dia * l["dias_mes"]
            total, l["tren"] = get_calculo_costo(tren, l, param.dias_mes, total)  # tren.get(l["equipo__equipo__familia_equipo_id"], 0) * param.horas_dia * l["dias_mes"]
            total, l["posesion"] = get_calculo_costo(posesion, l, param.dias_mes, total)  # posesion.get(l["equipo__equipo__familia_equipo_id"], 0) * param.horas_dia * l["dias_mes"]
            total, l["repara"] = get_calculo_costo(repara, l, param.dias_mes, total)  # repara.get(l["equipo__equipo__familia_equipo_id"], 0) * param.horas_dia * l["dias_mes"]
        totales[v[0]["obra_id"]] = decimal_format(total)

    return result, totales


def get_cc_on_periodo(periodo, totales):
    # Todas las obras implicadas en costos
    ccs = Obras.objects.filter(es_cc=True).values_list('id', 'codigo', 'prorratea_combustible', 'prorratea_manoobra',
                                                  'prorratea_materiales')
    # Ids de obras tipo CC (con costos prorrateables y sin)
    obras_ids = [x[0] for x in ccs]
    pro_combustible = [x[0] for x in ccs if x[2]]
    pro_manoobra = [x[0] for x in ccs if x[3]]
    pro_materiales = [x[0] for x in ccs if x[4]]

    # Busco las cabeceras (CC no prorrateable)
    no_prorrat = dict(ccs.filter(prorratea_combustible=False,
                                 prorratea_manoobra=False,
                                 prorratea_materiales=False).values_list('id', 'codigo'))

    # Defino el head del reporte
    report = []
    headers = [x for x in no_prorrat.values()]
    headers.insert(0, "TIPO DE COSTO")
    report.append(headers)

    # combustible
    combustible = dict(ccs.annotate(combustible=Sum(
        Case(
            When(
                partediario__fecha__gte=periodo.fecha_inicio,
                partediario__fecha__lte=periodo.fecha_fin,
                then='partediario__equipo__cant_combustible')
        )
    )
    ).values_list('id', 'combustible'))


    # Prorrateo de combustible
    report = calcular_item_costo(
        report,
        "Combustible",
        combustible,
        no_prorrat,
        pro_combustible, multiplicador=13.03)

    # Mano de obra
    mos = dict(CostoManoObra.objects.filter(periodo=periodo, obra_id__in=obras_ids).values_list('obra_id', 'monto'))
    report = calcular_item_costo(
        report,
        "Mano de obra",
        mos,
        no_prorrat,
        pro_manoobra
    )


    # subcontratos
    sub = dict(CostoSubContrato.objects.filter(periodo=periodo, obra_id__in=obras_ids).values_list('obra_id', 'monto'))
    report = calcular_item_costo(
        report,
        "Subcontratos",
        sub,
        no_prorrat
    )

    # gastos de equipos
    report = calcular_item_costo(
        report,
        "Utilización de equipos",
        totales,
        no_prorrat
    )

    # Materiales
    mat = dict(MaterialesTotal.objects.filter(periodo=periodo, obra__id__in=obras_ids).values_list('obra_id', 'monto'))
    report = calcular_item_costo(
        report,
        "Materiales",
        mat,
        no_prorrat,
        pro_materiales
    )

    # armamos la tabla de costos



    # Subtotales

    return report

