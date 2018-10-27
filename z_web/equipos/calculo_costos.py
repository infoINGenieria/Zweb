# coding: utf-8
from collections import defaultdict

from django.db.models import Count, Q

from equipos.models import AsistenciaEquipo, CostoEquipoValores, ParametrosGenerales
from core.models import Obras, Equipos


def get_stats_of_asistencia(periodo, centro_costo_id=None):
    """
    Calcula el informe de asistencia, indicando cantidad de dias de
    los equipos en los centro de costos.
    Si se indica centro_costo_id será filtro por centro de contro.
    :param periodo: Periodo del informe
    :return: Un queryset con el equipo, el CC y la cantidad de días.
    """
    if centro_costo_id:
        asistencias = AsistenciaEquipo.objects.filter(
            registros__centro_costo_id=centro_costo_id,
            dia__gte=periodo.fecha_inicio, dia__lte=periodo.fecha_fin)
    else:
        asistencias = AsistenciaEquipo.objects.filter(
            dia__gte=periodo.fecha_inicio, dia__lte=periodo.fecha_fin)
    registros = asistencias.values(
        'registros__equipo',
        'registros__centro_costo'
        ).annotate(
            dias=Count('registros__centro_costo')
        ).values(
            'registros__equipo',
            'registros__centro_costo',
            'dias'
        ).order_by()
    return registros, asistencias


def get_stats_of_asistencia_by_cc(periodo, centro_costo_id=None):

    registros, asistencias = get_stats_of_asistencia(periodo, centro_costo_id)
    parametros = ParametrosGenerales.vigente(periodo)

    equipos = Equipos.objects.filter(
        Q(excluir_costos_taller=False) | Q(pk__in=registros.values_list('registros__equipo', flat=True))
    )
    centro_costos = Obras.objects.filter(es_cc=True, pk__in=registros.values_list('registros__centro_costo', flat=True))
    processed = []

    for eq in equipos:
        records = filter(lambda a: a["registros__equipo"] == eq.pk, registros)
        valor = CostoEquipoValores.objects.vigente(eq, periodo)
        if valor:
            costo_hs = valor.costo_equipo_calculado / parametros.dias_por_mes / parametros.horas_por_dia
        else:
            costo_hs = 0
        processed.extend([
            {
                'equipo_id': eq.pk,
                'equipo': eq,
                'centro_costo': centro_costos.get(pk=x["registros__centro_costo"]),
                'centro_costo_id': x["registros__centro_costo"],
                'dias': x["dias"],
                'horas': parametros.horas_por_dia * x["dias"],
                'costo_hs': costo_hs,
                'costo_diario': costo_hs * parametros.horas_por_dia
            } for x in records
        ])

    return processed, asistencias


def get_stats_of_asistencia_summary(periodo):
    registros, asistencias = get_stats_of_asistencia_by_cc(periodo)

    report = {}
    for row in registros:
        data = report.get(row["centro_costo_id"], {})
        total_equipo = row["dias"] * row["costo_diario"]
        data["centro_costo"] = row["centro_costo"]
        data["un"] = row["centro_costo"].unidad_negocio.codigo if row["centro_costo"].unidad_negocio else ''
        if row["equipo"].es_alquilado:
            data["consumo_alquilados"] = data.get('consumo_alquilados', 0) + total_equipo
        else:  # propio
            data["consumo_propios"] = data.get('consumos_propios', 0) + total_equipo
        report[row["centro_costo_id"]] = data
    return report, asistencias
