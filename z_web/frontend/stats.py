from collections import defaultdict

from django.db.models import Count, When, Case, Sum

from costos.models import (LubricanteFluidosHidro, TrenRodaje, CostoPosesion, ReserveReparaciones, CostoParametro,
                           CostoManoObra, CostoSubContrato, MaterialesTotal)
from core.models import Obras
from registro.models import Partediario, Certificacion, AjusteCombustible, CertificacionInterna


def get_calculo_costo(costos, valores, horas_dia, total=0):
    val = costos.get(valores["registro_equipo__equipo__familia_equipo_id"], 0) * horas_dia * valores["dias_mes"]
    total += val
    return total, val


def calcular_item_costo(report, datos, no_prorrat, prorrat=None, multiplicador=1, ajuste={}):
    lista = []

    for x in no_prorrat:
        val = datos.get(x, 0) * multiplicador if datos.get(x, 0) else 0
        val += ajuste.get(x, 0)
        lista.append(val)
    report.append(lista)

    if not prorrat is None:
        lista_prorrat = []
        total_prorrateo = 0
        for x in prorrat:
            data = datos.get(x, 0)
            _ajuste = ajuste.get(x, 0)
            if data or _ajuste:
                total_prorrateo += (data if data else 0 * multiplicador) + _ajuste
        total_prorrateo /= len(no_prorrat)
        for x in no_prorrat:
            lista_prorrat.append(total_prorrateo)
        report.append(lista_prorrat)
    return report


def get_utilizacion_equipo(periodo):
    obras = list(Certificacion.objects.filter(periodo=periodo).values_list('obra_id', flat=True))
    obras += list(CertificacionInterna.objects.filter(periodo=periodo).values_list('obra_id', flat=True))
    if not obras:
        raise Certificacion.DoesNotExist
    qs = Partediario.objects.filter(
        fecha__lte=periodo.fecha_fin, fecha__gte=periodo.fecha_inicio, situacion__id=1, obra__in=obras).exclude(
        registro_equipo__equipo_id=1).exclude(registro_equipo__isnull=True).values(
        'registro_equipo__equipo_id', 'registro_equipo__equipo__n_interno',
        'obra__codigo', 'obra_id', 'registro_equipo__equipo__familia_equipo_id',
        'registro_equipo__equipo__familia_equipo__nombre').annotate(dias_mes=Count('id')).order_by(
        '-obra_id', '-registro_equipo__equipo__n_interno')

    processed = defaultdict(list)
    for result in qs:
        processed[result["obra__codigo"]].append(result)
    result = dict(processed.items())
    ids = list(set(x["registro_equipo__equipo__familia_equipo_id"] for x in qs))
    param = CostoParametro.objects.get(periodo=periodo)
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
            total, l["fluido"] = get_calculo_costo(lubris, l, param.horas_dia, total)
            total, l["tren"] = get_calculo_costo(tren, l, param.horas_dia, total)
            total, l["posesion"] = get_calculo_costo(posesion, l, param.horas_dia, total)
            total, l["repara"] = get_calculo_costo(repara, l, param.horas_dia, total)
        totales[v[0]["obra_id"]] = total

    return result, totales


def get_cc_on_periodo(periodo, totales):
    param = CostoParametro.objects.get(periodo=periodo)
    # Todas las obras implicadas en costos
    ccs1 = Certificacion.objects.select_related('obra').filter(
        periodo=periodo).values_list('obra_id', 'obra__codigo')
    serv = CertificacionInterna.objects.select_related('obra').filter(
        periodo=periodo).values_list('obra_id', 'obra__codigo')
    if not ccs1.exists() and not serv.exists():
        raise Certificacion.DoesNotExist

    # Busco las cabeceras (CC no prorrateable)
    no_prorrat = dict(ccs1)
    no_prorrat.update(dict(serv))

    ccs_pror = dict(Obras.objects.filter(prorratea_costos=True).exclude(
        pk__in=no_prorrat.keys()).values_list('id', 'codigo'))

    # Ids de obras tipo CC (con costos prorrateables y sin)
    obras_ids = list(no_prorrat.keys()) + list(ccs_pror.keys())

    # Defino el head del reporte

    headers = [x for x in no_prorrat.values()]
    headers.insert(0, "TIPO DE COSTO")
    tipo_costo_headers = ["Combustible", "Prorrateo de Combustible", "Mano de Obra", "Prorrateo de Mano de Obra", "Subcontratos" ,
     "Utilización de equipos", "Materiales", "Prorrateo de Materiales", "Totales"]

    values = []
    # combustible
    combustible = dict(Obras.objects.filter(pk__in=obras_ids).annotate(combustible=Sum(
        Case(
            When(
                partediario__fecha__gte=periodo.fecha_inicio,
                partediario__fecha__lte=periodo.fecha_fin,
                then='partediario__registro_equipo__cant_combustible')
        )
    )
    ).values_list('id', 'combustible'))

    # ajuste de combustible - temporal mientras se desarrolla combustible
    ajuste_combustible = dict(AjusteCombustible.objects.filter(
        periodo=periodo, obra_id__in=obras_ids).values_list('obra_id', 'valor'))

    # Prorrateo de combustible
    values = calcular_item_costo(
        values,
        combustible,
        no_prorrat,
        list(ccs_pror.keys()), multiplicador=param.precio_go, ajuste=ajuste_combustible)

    # Mano de obra
    mos = dict(CostoManoObra.objects.filter(periodo=periodo, obra_id__in=obras_ids).values_list('obra_id', 'monto'))
    values = calcular_item_costo(
        values,
        mos,
        no_prorrat,
        list(ccs_pror.keys())
    )


    # subcontratos
    sub = dict(CostoSubContrato.objects.filter(periodo=periodo, obra_id__in=obras_ids).values_list('obra_id', 'monto'))
    values = calcular_item_costo(
        values,
        sub,
        no_prorrat
    )

    # gastos de equipos
    values = calcular_item_costo(
        values,
        totales,
        no_prorrat
    )

    # Materiales
    mat = dict(MaterialesTotal.objects.filter(periodo=periodo, obra__id__in=obras_ids).values_list('obra_id', 'monto'))
    values = calcular_item_costo(
        values,
        mat,
        no_prorrat,
        list(ccs_pror.keys())
    )
    # armamos la tabla de costos
    totales = [sum(i) for i in zip(*values)]
    total = sum(totales)
    values.append(totales)
    report = []
    report.append(headers)
    i = 0
    for x in tipo_costo_headers:
        l = list()
        l.append(x)
        l.extend(values[i])
        report.append(l)
        i += 1

    return report, total, dict(zip(no_prorrat, totales))


def get_ventas_costos(periodo, totales_costos):
    """

    """
    ids = list(totales_costos.keys())
    obras = dict(Obras.objects.filter(id__in=ids).values_list('id', 'codigo'))
    cert = dict(Certificacion.objects.filter(periodo=periodo, obra_id__in=ids).values_list('obra_id', 'monto'))
    cert_interna = dict(CertificacionInterna.objects.filter(periodo=periodo, obra_id__in=ids).values_list('obra_id', 'monto'))
    report = [['CC', ], ['Costos', ], ['Certificaciones', ], ['Certif. Internas', ], ['Diferencia', ], ]
    total = {'t_costos': 0, 't_certif': 0, 't_servicios': 0, 't_diff': 0}
    for x in ids:
        report[0].append(obras.get(x, 0))
        report[1].append(totales_costos.get(x, 0))
        total["t_costos"] += totales_costos.get(x, 0)
        report[2].append(cert.get(x, 0))
        total["t_certif"] += cert.get(x, 0)
        report[3].append(cert_interna.get(x, 0))
        total["t_servicios"] += cert_interna.get(x, 0)
        row_t = cert.get(x, 0) - totales_costos.get(x, 0) + cert_interna.get(x, 0)
        report[4].append(row_t)
        total["t_diff"] += row_t
    return report, total
