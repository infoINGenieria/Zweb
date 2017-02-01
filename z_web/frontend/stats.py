from collections import defaultdict

from django.db.models import Count, When, Case, Sum
from django.utils.text import slugify

from costos.models import (LubricanteFluidosHidro, TrenRodaje, CostoPosesion, ReserveReparaciones, CostoParametro,
                           CostoManoObra, CostoSubContrato, MaterialesTotal)
from core.models import Obras
from registro.models import Partediario, Certificacion, AjusteCombustible, CertificacionInterna


def get_headers_costos():
    heads = ["Combustible", "Prorrateo de Combustible", "Mano de Obra", "Prorrateo de Mano de Obra",
             "Subcontratos", "Utilización de equipos", "Materiales", "Prorrateo de Materiales"]
    return [(slugify(x), x) for x in heads]


def get_limited_dict(orig, restr):
    if restr:
        # buscmos la intercepción de sus claves
        limit_cc = set(orig).intersection(restr)
        # actualizamos el dict
        orig = dict(filter(lambda i: i[0] in limit_cc, orig.items()))
    return orig


def get_calculo_costo(costos, valores, horas_dia, total=0):
    val = costos.get(valores["registro_equipo__equipo__familia_equipo_id"], 0) * horas_dia * valores["dias_mes"]
    total += val
    return total, val


def calcular_item_costo(report, datos, no_prorrat, limited_cc=None, prorrat=None, multiplicador=1,
                        absoluto={}, ajuste={}):
    """
    Función que completa el informe con los datos numéricos.
    :param report: list con todos los datos del reporte
    :param datos: datos sobre el sector del reporte
    :param no_prorrat: CC que no prorratean sus costos
    :param limited_cc: Si existe, especifica los centros de los que se desean visualizar
    :param prorrat: CC que prorratean costos
    :param multiplicador: multiplicados de costos (por ej, dato: litro de gasoil | multiplicadosr: precio del gasoil)
    :param absoluto: valor fijado del costo, si está presenta, no se calcula con el dato * multiplicador
    :param ajuste: valor de ajuste del calculo. Siempre es en $, se hace luego de la multiplicación
    :return: devuelve el reporte complete hasta el momento
    """
    lista = []
    centro_costo = limited_cc if limited_cc is not None else no_prorrat
    for x in centro_costo:
        abs = absoluto.get(x, 0)
        if not abs:
            val = datos.get(x, 0) * multiplicador if datos.get(x, 0) else 0
            val += ajuste.get(x, 0)
        else:
            val = abs
        lista.append(val)
    report.append(lista)

    if prorrat is not None:
        lista_prorrat = []
        total_prorrateo = 0
        for x in prorrat:
            abs = absoluto.get(x, 0)
            if not abs:
                data = datos.get(x, 0)
                _ajuste = ajuste.get(x, 0)
                if data or _ajuste:
                    total_prorrateo += (data if data else 0 * multiplicador) + _ajuste
            else:
                total_prorrateo += abs
        total_prorrateo /= len(no_prorrat)
        for x in centro_costo:
            lista_prorrat.append(total_prorrateo)
        report.append(lista_prorrat)
    return report


def get_utilizacion_equipo(periodo, limit_cc=None):
    obras = list(Certificacion.objects.filter(periodo=periodo).values_list('obra_id', flat=True))
    obras += list(CertificacionInterna.objects.filter(periodo=periodo).values_list('obra_id', flat=True))
    if not obras:
        raise Certificacion.DoesNotExist
    elif limit_cc:
        obras = set(obras).intersection(limit_cc)
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
    # cálculo de lubricantes
    lubris = dict(LubricanteFluidosHidro.objects.filter(
        periodo=periodo, familia_equipo_id__in=ids).values_list('familia_equipo', 'monto_hora'))
    # cálculo de tren
    tren = dict(TrenRodaje.objects.filter(periodo=periodo, familia_equipo_id__in=ids).values_list('familia_equipo',
                                                                                                  'monto_hora'))
    # cálculo de posesión
    posesion = dict(
        CostoPosesion.objects.filter(periodo=periodo, familia_equipo_id__in=ids).values_list('familia_equipo',
                                                                                             'monto_hora'))
    # cálculo de reparación
    repara = dict(
        ReserveReparaciones.objects.filter(periodo=periodo, familia_equipo_id__in=ids).values_list('familia_equipo',
                                                                                                   'monto_hora'))
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


def get_cc_on_periodo(periodo, equipos_totales, get_dict=False, limit_cc=None):
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

    limited_no_prorrat = None

    if limit_cc:
        limited_no_prorrat = get_limited_dict(no_prorrat, limit_cc)
        # Ids de obras tipo CC (con costos prorrateables y sin) limitadas a la busqueda
        obras_ids = list(limited_no_prorrat.keys()) + list(ccs_pror.keys())
    else:
        # Ids de obras tipo CC (con costos prorrateables y sin)
        obras_ids = list(no_prorrat.keys()) + list(ccs_pror.keys())

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

    # si existen valor (total) de combustible, lo pasamos en absoluto
    total_combustible = dict(AjusteCombustible.objects.filter(
        periodo=periodo, obra_id__in=obras_ids, costo_total__isnull=False).values_list('obra_id', 'costo_total'))

    # ajuste de combustible - temporal mientras se desarrolla combustible
    ajuste_combustible = dict(AjusteCombustible.objects.filter(
        periodo=periodo, obra_id__in=obras_ids, valor__isnull=False).values_list('obra_id', 'valor'))

    # Prorrateo de combustible
    values = calcular_item_costo(report=values, datos=combustible, no_prorrat=no_prorrat, limited_cc=limited_no_prorrat,
                                 prorrat=list(ccs_pror.keys()), multiplicador=param.precio_go,
                                 ajuste=ajuste_combustible, absoluto=total_combustible)

    # Mano de obra
    mos = dict(CostoManoObra.objects.filter(periodo=periodo, obra_id__in=obras_ids).values_list('obra_id', 'monto'))
    values = calcular_item_costo(report=values, datos=mos, no_prorrat=no_prorrat, limited_cc=limited_no_prorrat,
                                 prorrat=list(ccs_pror.keys()))

    # subcontratos
    sub = dict(CostoSubContrato.objects.filter(periodo=periodo, obra_id__in=obras_ids).values_list('obra_id', 'monto'))
    values = calcular_item_costo(report=values, datos=sub, no_prorrat=no_prorrat, limited_cc=limited_no_prorrat)

    # gastos de equipos
    values = calcular_item_costo(report=values, datos=equipos_totales, no_prorrat=no_prorrat,
                                 limited_cc=limited_no_prorrat)

    # Materiales
    mat = dict(MaterialesTotal.objects.filter(periodo=periodo, obra__id__in=obras_ids).values_list('obra_id', 'monto'))
    values = calcular_item_costo(report=values, datos=mat, no_prorrat=no_prorrat, limited_cc=limited_no_prorrat,
                                 prorrat=list(ccs_pror.keys()))

    # armamos la tabla de costos
    totales = [sum(i) for i in zip(*values)]

    tipo_costo_headers = get_headers_costos()

    columns = list(no_prorrat if limited_no_prorrat is None else limited_no_prorrat)
    if get_dict:
        result = {}
        i = 0
        for pk in columns:
            j = 0
            data = {}
            for costo in [x[0] for x in tipo_costo_headers]:  # solo keys
                data[costo] = values[j][i]
                j += 1
            result[pk] = data
            i += 1
        return result, dict(zip(columns, totales))
    else:
        headers = ["TIPO DE COSTO", ]
        # si están limitados, usamos esos, sino todas los CC
        if limit_cc:
            # Defino el head del reporte
            headers.extend([v for k, v in no_prorrat.items() if k in limited_no_prorrat])
        else:
            # Defino el head del reporte
            headers.extend([x for x in no_prorrat.values()])

        total = sum(totales)
        values.append(totales)
        report = []
        report.append(headers)
        i = 0
        for x in [x[1] for x in tipo_costo_headers] + ["Totales", ]:  # solo values
            l = list()
            l.append(x)
            l.extend(values[i])
            report.append(l)
            i += 1

        return report, total, dict(zip(columns, totales))


def get_ventas_costos(periodo, totales_costos, get_dict=False):
    """
    Devuelve los costos vs certificaciones y sus diferencias para los totales de costos pasados por parámetro.
    """
    ids = list(totales_costos.keys())
    obras = dict(Obras.objects.filter(id__in=ids).values_list('id', 'codigo'))
    cert = dict(Certificacion.objects.filter(periodo=periodo, obra_id__in=ids).values_list('obra_id', 'monto'))
    cert_interna = dict(
        CertificacionInterna.objects.filter(periodo=periodo, obra_id__in=ids).values_list('obra_id', 'monto'))
    total = {'t_costos': 0, 't_certif': 0, 't_servicios': 0, 't_diff': 0}
    for x in ids:
        total["t_costos"] += totales_costos.get(x, 0)
        total["t_certif"] += cert.get(x, 0)
        total["t_servicios"] += cert_interna.get(x, 0)
        row_t = cert.get(x, 0) - totales_costos.get(x, 0) + cert_interna.get(x, 0)
        total["t_diff"] += row_t
    if get_dict:
        report = {}
        for x in ids:
            report[x] = {
                'costos': totales_costos.get(x, 0),
                'certificaciones': cert.get(x, 0),
                'certif_internas': cert_interna.get(x, 0),
                'diferencia': cert.get(x, 0) - totales_costos.get(x, 0) + cert_interna.get(x, 0)
            }
        return report, total
    else:
        report = [['CC', ], ['Costos', ], ['Certificaciones', ], ['Certif. Internas', ], ['Diferencia', ], ]
        for x in ids:
            report[0].append(obras.get(x, 0))
            report[1].append(totales_costos.get(x, 0))
            report[2].append(cert.get(x, 0))
            report[3].append(cert_interna.get(x, 0))
            row_t = cert.get(x, 0) - totales_costos.get(x, 0) + cert_interna.get(x, 0)
            report[4].append(row_t)
        return report, total
