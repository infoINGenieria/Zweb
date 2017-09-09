# coding: utf-8
from collections import defaultdict

from django.utils.formats import date_format
from django.utils import translation

from registro.models import Registro, RegistroEquipo
from core.models import Operarios

from zweb_utils.dates import daterange


def gen_report_detalle_hora(operario_id, date_start, date_end, cct):
    """
    SELECT
        R.*,
        PD.fecha AS fec, PD.multifuncion AS multi, PD.observaciones,
        PD.comida, PD.vianda, PD.vianda_desa,
        O.nombre AS NOM_OP,
        IH.*,
        S.situacion, S.id AS id_sit,
        OB.codigo AS obra

        FROM partediario PD
        LEFT JOIN obras OB ON PD.obra = OB.id
        LEFT JOIN operarios O ON PD.operario = O.id
        LEFT JOIN informes_horas IH ON PD.operario = IH.id_operario
        LEFT JOIN registro R ON PD.id = R.partediario_id
        LEFT JOIN situacion S ON PD.situacion = S.id

        where IH.id = $P{id_informe} and  PD.fecha <= IH.hasta_f and PD.fecha >= IH.desde_f
        order by PD.fecha asc

        HS. NORMALES	HS. EXTRAS 50%	HS. EXTRAS 100%	HS. VIAJE
        HS. ENFERME	HS. FERIADO	AY. ALIMEN	VIANDA	VIANDA DOBLE	VIANDA MS

    """
    if cct == 'UOCRA':
        return []

    translation.activate(translation.get_language())

    report = [
        ['DÍA', 'FECHA', 'SALIDA BASE', 'ENTRADA OBRA',
        'SALIDA OBRA', 'ENTRADA OBRA', 'SALIDA OBRA', 'ENTRADA BASE',
        'HS. NORMALES', 'HS. EXTRAS 50%', 'HS. EXTRAS 100%	HS.',
        'VIAJE', 'HS TAREA', 'HS TOTAL']
    ]

    # operario = Operarios.objects.get(pk=operario_id)
    registros = list(Registro.objects.select_related('partediario').filter(
        partediario__operario_id=operario_id,
        partediario__fecha__gte=date_start,
        partediario__fecha__lte=date_end).values_list(
            'partediario__fecha',
            'hs_salida', 'hs_inicio', 'hs_ialmuerzo', 'hs_falmuerzo', 'hs_fin', 'hs_llegada',
            'hs_normal', 'hs_50', 'hs_100', 'hs_viaje', 'hs_tarea', 'hs_total',
        ))

    data = defaultdict()
    for reg in registros:
        data[reg[0]] = reg

    for dia in daterange(date_start, date_end, inclusive=True):
        line = data.get(dia, False)
        row = [date_format(dia, 'l'), date_format(dia, 'd/m/Y')]
        if line:
            row.extend(line[1:])
        else:
            row.extend([''] * 12)
        report.append(row)

    return report
