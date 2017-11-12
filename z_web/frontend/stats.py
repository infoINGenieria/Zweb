# coding: utf-8
from collections import defaultdict
from decimal import Decimal as D

from django.db.models import Count, When, Case, Sum
from django.utils.text import slugify

from costos.models import CostoParametro, Costo, CostoTipo
from core.models import Obras
from registro.models import Partediario, CertificacionReal, AjusteCombustible, CertificacionInterna


def get_headers_costos():
    """
    Esto devuelve las etiquetas para los costos.

    TODO: hacer esto dinámico. Ver como determinar que costos pueden prorratearse
    """
    heads = ["Combustible", "Prorrateo de Combustible", ]
    for tipo in CostoTipo.objects.filter(relacionado_con='cc'):
        heads += [tipo.nombre, "Prorrateo de {}".format(tipo.nombre)]

    heads += ["Utilización de equipos"]
    return [(slugify(x), x) for x in heads]


def get_limited_dict(orig, restr):
    if restr:
        # buscmos la intercepción de sus claves
        limit_cc = set(orig).intersection(restr)
        # actualizamos el dict
        orig = dict(filter(lambda i: i[0] in limit_cc, orig.items()))
    return orig


def get_calculo_costo(costos, valores, horas_dia, total=0):
    costo = costos.get(valores["registro_equipo__equipo__familia_equipo_id"], D('0'))
    val = costo * horas_dia * valores["dias_mes"]
    total += val
    return total, val


def float_to_decimal(values):
    for j in range(0, len(values)):
        for p in range(0, len(values[j])):
            _aux = values[j][p]
            if not isinstance(_aux, D):
                values[j][p] = D('{}'.format(_aux))
    return values


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
    """
    Este método calcula los costos relacionados con los equipos. Para ello, obtiene
    los equipos que se utilizaron y la cantidad de días. Luego
    se calculan los costos por equipo utilizando los costos asociados a la familia x la cantidad de días de uso.
    """
    cc_unidad = Obras.get_centro_costos_ms()
    obras = list(CertificacionReal.objects.filter(
        periodo=periodo, obra__in=cc_unidad).values_list('obra_id', flat=True))
    obras += list(CertificacionInterna.objects.filter(
        periodo=periodo, obra__in=cc_unidad).values_list('obra_id', flat=True))
    if not obras:
        raise CertificacionReal.DoesNotExist
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

    costos_dict = {}
    for tipo in CostoTipo.objects.filter(relacionado_con='eq'):
        familia_costo = dict(
            Costo.objects.filter(tipo_costo=tipo, periodo=periodo,
                                 familia_equipo_id__in=ids).values_list('familia_equipo', 'monto_hora'))
        costos_dict[tipo.codigo] = familia_costo

    totales = dict()
    for obra, valores in result.items():
        total = 0
        for valor in valores:
            for costo, costo_valor in costos_dict.items():
                total, valor[costo] = get_calculo_costo(costo_valor, valor, param.horas_dia, total)
        totales[valores[0]["obra_id"]] = total

    return result, totales


def get_cc_on_periodo(periodo, equipos_totales, get_dict=False, limit_cc=None):
    """
    Este método genera el resumen de costos de los distintas CC.
    """
    cc_unidad = Obras.get_centro_costos_ms()
    param = CostoParametro.objects.get(periodo=periodo)
    # Todas las obras implicadas en costos (de la unidad de negocio del usuario)
    ccs1 = CertificacionReal.objects.select_related('obra').filter(
        periodo=periodo, obra__in=cc_unidad).values_list('obra_id', 'obra__codigo')
    serv = CertificacionInterna.objects.select_related('obra').filter(
        periodo=periodo, obra__in=cc_unidad).values_list('obra_id', 'obra__codigo')
    if not ccs1.exists() and not serv.exists():
        raise CertificacionReal.DoesNotExist

    # Busco las cabeceras (CC no prorrateable)
    no_prorrat = dict(ccs1)
    no_prorrat.update(dict(serv))

    ccs_pror = dict(cc_unidad.filter(prorratea_costos=True).exclude(
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

    # TODO: El caso del combustible necesita una vuelta de rosca, luego de implementar esa área.
    # Actualmente, está bastante hardcodeado y rigido. Seguramente, este costo se obtendrá de ese subsistema.

    # combustible
    combustible = dict(cc_unidad.filter(pk__in=obras_ids).annotate(combustible=Sum(
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

    for tipo in CostoTipo.objects.filter(relacionado_con='cc'):
        costo_data = dict(Costo.objects.filter(
            periodo=periodo, centro_costo__in=obras_ids, tipo_costo=tipo).values_list('centro_costo_id', 'monto_total'))
        values = calcular_item_costo(
            report=values,
            datos=costo_data,
            no_prorrat=no_prorrat,
            limited_cc=limited_no_prorrat,
            prorrat=list(ccs_pror.keys())
        )

    # adicionalmente, añadimos los costos de equipos
    values = calcular_item_costo(
        report=values, datos=equipos_totales,
        no_prorrat=no_prorrat,
        limited_cc=limited_no_prorrat)

    # normalizamos valores: tipo float lo convertimos a Decimal
    values = float_to_decimal(values)

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
            fila = list()
            fila.append(x)
            fila.extend(values[i])
            # si toda la fila es 0, no la incluyo.
            if sum(fila[1:]) != 0:
                report.append(fila)
            i += 1

        return report, total, dict(zip(columns, totales))


def get_ventas_costos(periodo, totales_costos, get_dict=False):
    """
    Devuelve los costos vs certificaciones y sus diferencias para los totales de costos pasados por parámetro.
    """
    cc_unidad = Obras.get_centro_costos_ms()
    ids = list(totales_costos.keys())
    obras = dict(cc_unidad.filter(id__in=ids).values_list('id', 'codigo'))
    # Como las certificaciones tiene ítems, debemos obtener su sumatoria
    cert = dict(
        CertificacionReal.objects.filter(periodo=periodo, obra_id__in=ids).annotate(
            total=Sum('items__monto')).values_list('obra_id', 'total'))
    cert_interna = dict(
        CertificacionInterna.objects.filter(periodo=periodo, obra_id__in=ids).values_list('obra_id', 'monto'))
    total = {'t_costos': D(0), 't_certif': D(0), 't_servicios': D(0), 't_diff': D(0)}
    for x in ids:
        t_costos = D(totales_costos.get(x, 0))
        t_certif = D(cert.get(x, 0))
        t_servicios = D(cert_interna.get(x, 0))
        total["t_costos"] += t_costos
        total["t_certif"] += t_certif
        total["t_servicios"] += t_servicios
        row_t = t_certif - t_costos + t_servicios
        total["t_diff"] += row_t
    if get_dict:
        report = {}
        for x in ids:
            report[x] = {
                'costos': D(totales_costos.get(x, 0)),
                'certificaciones': D(cert.get(x, 0)),
                'certif_internas': D(cert_interna.get(x, 0)),
                'diferencia': D(cert.get(x, 0)) - D(totales_costos.get(x, 0)) + D(cert_interna.get(x, 0))
            }
        return report, total
    else:
        report = [['CC', ], ['Costos', ], ['Certificaciones', ], ['Certif. Internas', ], ['Diferencia', ], ]
        for x in ids:
            report[0].append(obras.get(x, 0))
            report[1].append(D(totales_costos.get(x, 0)))
            report[2].append(D(cert.get(x, 0)))
            report[3].append(D(cert_interna.get(x, 0)))
            # TODO: ir pasando todo a Decimal
            row_t = D(cert.get(x, 0)) - D(totales_costos.get(x, 0)) + D(cert_interna.get(x, 0))
            report[4].append(row_t)
        return report, total
