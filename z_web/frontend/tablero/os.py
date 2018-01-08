# coding: utf-8
"""
Tablero de control para Obras de superficie.
"""
import time
from decimal import Decimal as D

from django.core.cache import cache
from django.db.models import Sum, F, Min, Max
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist

from core.models import Obras
from organizacion.models import UnidadNegocio
from parametros.models import Periodo
from presupuestos.models import Presupuesto, Revision
from registro.models import CertificacionItem, Certificacion
from costos.models import Costo, AvanceObra, Costo
from proyecciones.models import ProyeccionAvanceObra, ProyeccionCertificacion, ProyeccionCosto


class MarkUpColumn(object):
    subtotal_venta = 0
    subtotal_costos_previstos = 0
    subtotal_costo_industrial = 0

    def __init__(self, revision):
        self.revision = revision

    def _2D(self, value):
        if isinstance(value, D):
            return value.quantize(D("0.01"))
        D("{}".format(value)).quantize(D("0.01"))

    @property
    def subtotal_costo(self):
        return self._2D(
            self.subtotal_costo_industrial + self.impuestos_y_contribuciones +
            self.costo_financiero_e_imprevistos)

    @property
    def impuestos_y_contribuciones(self):
        return self._2D(
            self.revision.sellado_pesos + self.revision.impuesto_ganancias_pesos +
            self.revision.ingresos_brutos_pesos + self.revision.impuestos_cheque_pesos
        )

    @property
    def impuestos_y_contribuciones_perc(self):
        return self._2D(self.impuestos_y_contribuciones / self.subtotal_costo_industrial * 100)

    @property
    def costo_financiero_e_imprevistos(self):
        return self._2D(self.revision.imprevistos_pesos +
                        self.revision.costo_financiero_pesos)

    @property
    def costo_financiero_e_imprevistos_perc(self):
        return self._2D(self.costo_financiero_e_imprevistos / self.subtotal_costo_industrial * 100)

    @property
    def ganancias_despues_impuestos(self):
        return self._2D(self.revision.ganancias)

    @property
    def ganancias_despues_impuestos_perc(self):
        return self._2D(self.ganancias_despues_impuestos / self.subtotal_costo_industrial * 100)

    @property
    def margen_bruto(self):
        return self._2D(
            self.costo_financiero_e_imprevistos + self.impuestos_y_contribuciones +
            self.ganancias_despues_impuestos)

    @property
    def margen_bruto_perc(self):
        return self._2D(self.margen_bruto / self.subtotal_costo_industrial * 100)


    def set_subtotal_costo_industrial(self, costos_estructurales):
        self.subtotal_costo_industrial = self._2D(costos_estructurales + self.subtotal_costos_previstos)
        return self.subtotal_costo_industrial

    def to_dict(self):
        return {
            "impuestos_y_contribuciones": self.impuestos_y_contribuciones,
            "impuestos_y_contribuciones_perc": self.impuestos_y_contribuciones_perc,
            "costo_financiero_e_imprevistos": self.costo_financiero_e_imprevistos,
            "costo_financiero_e_imprevistos_perc": self.costo_financiero_e_imprevistos_perc,
            "ganancias_despues_impuestos": self.ganancias_despues_impuestos,
            "ganancias_despues_impuestos_perc": self.ganancias_despues_impuestos_perc,
            "margen_bruto": self.margen_bruto,
            "margen_bruto_perc": self.margen_bruto_perc
    }

class MarkUpColumnEstimado(MarkUpColumn):
    """
    En la columna de estimados, algunas formulas cambian.
    """

    @property
    def impuestos_y_contribuciones(self):
        return self._2D(
            self.revision.sellado_pesos + (
                (self.revision.ingresos_brutos + self.revision.impuestos_cheque) * self.subtotal_venta / 100
            ) + (self.ganancias_despues_impuestos * self.revision.impuestos_ganancias / 100)
        )

    @property
    def costo_financiero_e_imprevistos(self):
        return self._2D(
            self.revision.imprevistos_pesos + (
                self.revision.costo_financiero * self.subtotal_costo_industrial / 100))

    @property
    def ganancias_despues_impuestos(self):
        calc = self.subtotal_venta - (
            self.subtotal_costo_industrial + #I30
            self.costo_financiero_e_imprevistos +  #I33
            self.revision.sellado_pesos +  # $'Ppto. aprobado - R2'.I75
            ((self.revision.ingresos_brutos + self.revision.impuestos_cheque) * self.subtotal_venta / 100)
        ) / (1 + (self.revision.impuestos_ganancias / 100))
        return self._2D(calc)


class MarkUp(object):

    def __init__(self, revision, revision_b0):
        self.revision = revision
        self.revision_b0 = revision_b0
        self.estimado = MarkUpColumnEstimado(revision)
        self.presupuesto = MarkUpColumn(revision)
        self.comercial = MarkUpColumn(revision_b0)

    def to_dict(self):
        return {
            "estimado": self.estimado.to_dict(),
            "presupuesto": self.presupuesto.to_dict(),
            "comercial": self.comercial.to_dict()
        }

def generar_tabla_tablero(obra, periodo):
    # primero, si lo guarde en cache, uso ese!! 30 segundos de cache
    key_cache = "tablero_{}_{}".format(obra.pk, periodo.pk)
    data_table = cache.get(key_cache)
    if data_table:
        return data_table

    presupuesto = Presupuesto.objects.filter(
        centro_costo=obra).latest('fecha')

    try:
        revision = presupuesto.revisiones.filter(fecha__lte=periodo.fecha_fin).latest('fecha')
    except Revision.DoesNotExist:
        raise ValueError("Seleccione un periodo posterior. No existen revisiones anteriores a la fecha de fin del periodo")
    revision_b0 = presupuesto.revisiones.get(version=0)

    markup = MarkUp(revision, revision_b0)

    data_table = {}

    # acumulados
    venta = {}

    certificaciones = Certificacion.objects.filter(
        obra=obra, periodo__fecha_fin__lte=periodo.fecha_fin)
    venta["acumulado"] = {
        "venta_contractual": certificaciones.filter(items__concepto="basica").aggregate(total=Sum('items__monto'))["total"] or 0,
        "ordenes_cambio": certificaciones.filter(items__concepto="cambios").aggregate(total=Sum('items__monto'))["total"] or 0,
        "reajustes_precios": certificaciones.filter(items__concepto="reajuste").aggregate(total=Sum('items__monto'))["total"] or 0,
        "reclamos_reconocidos": certificaciones.filter(items__concepto="reclamos").aggregate(total=Sum('items__monto'))["total"] or 0
    }
    venta["acumulado"]["subtotal"] = sum(venta["acumulado"].values())
    # en el futuro
    proyecciones_cert = ProyeccionCertificacion.objects.filter(
        centro_costo=obra, periodo__fecha_inicio__gt=periodo.fecha_fin)
    # faltante
    venta["faltante_estimado"] = {
        # "venta_contractual": proyecciones_cert.filter(
        #     items__concepto="basica").aggregate(total=Sum('items__monto'))["total"] or 0,
        # "ordenes_cambio": proyecciones_cert.filter(
        #     items__concepto="cambios").aggregate(total=Sum('items__monto'))["total"] or 0,
        # "reajustes_precios": proyecciones_cert.filter(
        #     items__concepto="reajuste").aggregate(total=Sum('items__monto'))["total"] or 0,
        # "reclamos_reconocidos": proyecciones_cert.filter(
        #     items__concepto="reclamos").aggregate(total=Sum('items__monto'))["total"] or 0
        "venta_contractual": proyecciones_cert.all().aggregate(total=Sum('items__monto'))["total"] or 0,
        "ordenes_cambio": 0,
        "reajustes_precios":  0,
        "reclamos_reconocidos":  0
    }
    venta["faltante_estimado"]["subtotal"] = sum(venta["faltante_estimado"].values())

    # faltante ppto
    venta["faltante_presupuesto"] = {
        "venta_contractual": revision.total_venta - venta["acumulado"]["venta_contractual"],
        "ordenes_cambio": (revision.ordenes_cambio or 0) - venta["acumulado"]["ordenes_cambio"],
        "reajustes_precios": (revision.reajustes_precio or 0) - venta["acumulado"]["reajustes_precios"],
        "reclamos_reconocidos": (revision.reclamos_reconocidos or 0)  - venta["acumulado"]["reclamos_reconocidos"]
    }
    venta["faltante_presupuesto"]["subtotal"] = sum(venta["faltante_presupuesto"].values())

    # totales
    venta["estimado"] = {
        "venta_contractual": venta["acumulado"]["venta_contractual"] + venta["faltante_estimado"]["venta_contractual"],
        "ordenes_cambio": venta["acumulado"]["ordenes_cambio"] + venta["faltante_estimado"]["ordenes_cambio"],
        "reajustes_precios": venta["acumulado"]["reajustes_precios"] + venta["faltante_estimado"]["reajustes_precios"],
        "reclamos_reconocidos": venta["acumulado"]["reclamos_reconocidos"] + venta["faltante_estimado"]["reclamos_reconocidos"],
    }
    markup.estimado.subtotal_venta = sum(venta["estimado"].values())
    venta["estimado"]["subtotal"] = markup.estimado.subtotal_venta

    # totales presupuesto
    venta["presupuesto"] = {
        "venta_contractual": revision.venta_contractual_b0 or 0,
        "ordenes_cambio": revision.ordenes_cambio or 0,
        "reajustes_precios": revision.reajustes_precio or 0,
        "reclamos_reconocidos": revision.reclamos_reconocidos or 0,
    }
    markup.presupuesto.subtotal_venta = sum(venta["presupuesto"].values())
    venta["presupuesto"]["subtotal"] = markup.presupuesto.subtotal_venta

    # totales base 9
    venta["comercial"] = {
        "venta_contractual": revision_b0.venta_contractual_b0 or 0,
        "ordenes_cambio": revision_b0.ordenes_cambio or 0,
        "reajustes_precios": revision_b0.reajustes_precio or 0,
        "reclamos_reconocidos": revision_b0.reclamos_reconocidos or 0,
    }
    markup.comercial.subtotal_venta = sum(venta["comercial"].values())
    venta["comercial"]["subtotal"] = markup.comercial.subtotal_venta

    data_table["venta"] = venta

    costos = {}

    # acumulado de costos reales
    costos_reales = dict(Costo.objects.filter(
        centro_costo=obra,
        periodo__fecha_fin__lte=periodo.fecha_fin).values(
            'tipo_costo__nombre').annotate(
                total=Sum('monto_total')).values_list(
                    'tipo_costo__nombre', 'total').order_by())
    costos_reales["subtotal"] = sum(costos_reales.values())

    # Faltante estimado son las proyecciones de costos

    proyeccion_costo_ultimo_ajuste = ProyeccionCosto.objects.filter(
        centro_costo=obra, periodo__fecha_fin__lte=periodo.fecha_fin).order_by(
            '-periodo__fecha_fin').first()

    costos_proyectados = dict(proyeccion_costo_ultimo_ajuste.items.values(
        'tipo_costo__nombre').annotate(
            total=Sum('monto')).values_list('tipo_costo__nombre', 'total').order_by())
    costos_proyectados["subtotal"] = sum(costos_proyectados.values())

    # Total presupuesto: busco el valor del item del presupuesto (directo e indirecto)
    costos_total_presupuesto = dict(
        revision.items.values('tipo__nombre').annotate(
            total=Sum('pesos') + (Sum('dolares') * F('revision__valor_dolar'))
        ).values_list('tipo__nombre', 'total').order_by()
    )
    costos_total_presupuesto["subtotal"] = sum(costos_total_presupuesto.values())

    # Total comercial: busco el valor del items del presupuesto Base 9
    costos_total_comercial = dict(
        revision_b0.items.values('tipo__nombre').annotate(
            total=Sum('pesos') + (Sum('dolares') * F('revision__valor_dolar'))
        ).values_list('tipo__nombre', 'total').order_by()
    )
    costos_total_comercial["subtotal"] = sum(costos_total_comercial.values())

    # Debemos completar con 0 todos las diferencias de claves entre los dict.
    claves_costos = set(
        list(costos_reales.keys()) + list(costos_proyectados.keys()) +
        list(costos_total_presupuesto.keys()) + list(costos_total_comercial.keys())
    )
    claves_costos.remove("subtotal")
    costos_faltante_presupuesto = {}
    costos_total_estimado = {}

    for costo_key in claves_costos:
        for dicc in (costos_reales, costos_proyectados, costos_total_presupuesto, costos_total_comercial):
            dicc[costo_key] = dicc.get(costo_key, 0)
        # aprovecho el bucle para crear los dict calculados
        # Faltante presupuesto: es la diferencia del costo del presupuesto - acumulado
        costos_faltante_presupuesto[costo_key] = costos_total_presupuesto[costo_key] - costos_reales[costo_key]
        # Total estimado: el acumulado + faltante estimado
        costos_total_estimado[costo_key] = costos_reales[costo_key] + costos_proyectados[costo_key]

    # calculos subtotales
    costos_faltante_presupuesto["subtotal"] = sum(list(costos_faltante_presupuesto.values()))
    costos_total_estimado["subtotal"] = sum(list(costos_total_estimado.values()))
    costos["acumulado"] = costos_reales
    costos["faltante_estimado"] = costos_proyectados
    costos["faltante_presupuesto"] = costos_faltante_presupuesto
    costos["estimado"] = costos_total_estimado
    costos["presupuesto"] = costos_total_presupuesto
    costos["comercial"] = costos_total_comercial

    # guardo en el markup los subtotales previstos
    markup.estimado.subtotal_costos_previstos = costos_total_estimado["subtotal"]
    markup.presupuesto.subtotal_costos_previstos = costos_total_presupuesto["subtotal"]
    markup.comercial.subtotal_costos_previstos = costos_total_comercial["subtotal"]

    data_table["costos"] = costos

    # Estructura de Costos
    estructura_costos = {
        'presupuesto': {
            "contingencia": revision.contingencia or 0,
            "estructura": revision.estructura_no_ree or 0,
            "avales_gtia_seguros": (
                (revision.aval_por_anticipos or 0) +
                (revision.seguro_caucion or 0) +
                (revision.seguro_5 or 0) +
                (revision.aval_por_cumplimiento_contrato or 0) +
                (revision.aval_por_cumplimiento_garantia or 0)
            )
        },
        "comercial": {
            "contingencia": revision_b0.contingencia or 0,
            "estructura": revision_b0.estructura_no_ree or 0,
            "avales_gtia_seguros": (
                (revision_b0.aval_por_anticipos or 0) +
                (revision_b0.seguro_caucion or 0) +
                (revision_b0.seguro_5 or 0) +
                (revision_b0.aval_por_cumplimiento_contrato or 0) +
                (revision_b0.aval_por_cumplimiento_garantia or 0)
            )
        }
    }
    # estimado y presupuesto son iguales acá, pero no sus subtotales
    estructura_costos["estimado"] = estructura_costos["presupuesto"].copy()

    # subtotales industriales
    estructura_costos["presupuesto"]["subtotal"] = markup.presupuesto.set_subtotal_costo_industrial(sum(estructura_costos["presupuesto"].values()))
    estructura_costos["estimado"]["subtotal"] = markup.estimado.set_subtotal_costo_industrial(sum(estructura_costos["estimado"].values()))
    estructura_costos["comercial"]["subtotal"] = markup.comercial.set_subtotal_costo_industrial(sum(estructura_costos["comercial"].values()))
    data_table["estructura_costos"] = estructura_costos

    # añadimos a la parte de costos, el calculo del total de los costos
    # costos industrial + impuestos y contribuciones + costo financiero e imprevistos
    # estos primeros son iguales a los subtotales
    costos["acumulado"]["total_costos"] = costos["acumulado"]["subtotal"]
    costos["faltante_estimado"]["total_costos"] = costos["faltante_estimado"]["subtotal"]
    costos["faltante_presupuesto"]["total_costos"] = costos["faltante_presupuesto"]["subtotal"]
    # estos dependen del markup
    costos["estimado"]["total_costos"] = markup.estimado.subtotal_costo
    costos["presupuesto"]["total_costos"] = markup.presupuesto.subtotal_costo
    costos["comercial"]["total_costos"] = markup.comercial.subtotal_costo

    # MARK UP
    data_table["markup"] = markup.to_dict()
    data_table["revision"] = model_to_dict(revision)

    # guardo en cache esto por 30 segundos
    cache.set(key_cache, data_table, 30)
    return data_table


def datetime_to_epoch(date):
    return int(time.mktime(date.timetuple())) * 1000


def get_certificacion_graph(obra, periodo):
    # buscar linea base
    line_base = ProyeccionCertificacion.objects.filter(
        centro_costo=obra, es_base=True).order_by('-base_numero').first()

    # buscar certificaciones reales, y completar con la ultima revision
    certificaciones = Certificacion.objects.filter(
        obra=obra, periodo__fecha_fin__lt=periodo.fecha_fin)

    revision = ProyeccionCertificacion.objects.filter(
        centro_costo=obra).order_by('-periodo__fecha_fin').first()

    # bucle por los periodos de la proyección

    periodo_range = ProyeccionCertificacion.objects.filter(
        centro_costo=obra).aggregate(
            ini_fecha=Min('items__periodo__fecha_fin'),
            fin_fecha=Max('items__periodo__fecha_fin'))

    cert_base = dict(line_base.items.values_list('periodo', 'monto'))
    cert_real = dict([(cert.periodo_id, cert.total) for cert in certificaciones])
    cert_revision = dict(revision.items.values_list('periodo', 'monto'))

    data_real = []
    data_proy = []

    for periodo in Periodo.objects.filter(
            fecha_fin__gte=periodo_range["ini_fecha"],
            fecha_fin__lte=periodo_range["fin_fecha"]).order_by('fecha_fin'):
        # lo obtengo de la linea base
        data_proy.append({
            'x': datetime_to_epoch(periodo.fecha_fin),
            'y': cert_base.get(periodo.pk, 0)
        })
        # lo obtengo de la certificaciones, si no existe, de la ultima revisión o 0
        data_real.append({
            'x': datetime_to_epoch(periodo.fecha_fin),
            'y': cert_real.get(periodo.pk, cert_revision.get(periodo.pk, 0))
        })
    return [
        {
            'key': "Certificación Proyectada",
            'values': data_proy,
            'color': '#2ca02c'
        },
        {
            'key': "Certificación Real",
            'values': data_real,
            'color': '#ff7f0e'
        },
    ]

def get_costos_graph(obra, periodo):
    # buscar linea base
    line_base = ProyeccionCosto.objects.filter(
        centro_costo=obra, es_base=True).order_by('-base_numero').first()

    # buscar costos reales, y completar con la ultima revision
    costos = Costo.objects.filter(
        centro_costo=obra, periodo__fecha_fin__lt=periodo.fecha_fin)

    revision = ProyeccionCosto.objects.filter(
        centro_costo=obra).order_by('-periodo__fecha_fin').first()

    # bucle por los periodos de la proyección
    periodo_range = ProyeccionCosto.objects.filter(
        centro_costo=obra).aggregate(
            ini_fecha=Min('items__periodo__fecha_fin'),
            fin_fecha=Max('items__periodo__fecha_fin'))

    costo_base = dict(line_base.items.values_list('periodo', 'monto'))
    costo_real = dict([(costo.periodo_id, costo.monto_total) for costo in costos])
    costo_revision = dict(revision.items.values_list('periodo', 'monto'))

    data_real = []
    data_proy = []

    for periodo in Periodo.objects.filter(
            fecha_fin__gte=periodo_range["ini_fecha"],
            fecha_fin__lte=periodo_range["fin_fecha"]).order_by('fecha_fin'):
        # lo obtengo de la linea base
        data_proy.append({
            'x': datetime_to_epoch(periodo.fecha_fin),
            'y': costo_base.get(periodo.pk, 0)
        })
        # lo obtengo de la costos, si no existe, de la ultima revisión o 0
        data_real.append({
            'x': datetime_to_epoch(periodo.fecha_fin),
            'y': costo_real.get(periodo.pk, costo_revision.get(periodo.pk, 0))
        })
    return [
        {
            'key': "Proyección de costos",
            'values': data_proy,
            'color': '#2ca02c'
        },
        {
            'key': "Costos reales",
            'values': data_real,
            'color': '#ff7f0e'
        },
    ]


def get_avances_graph(obra, periodo):
    # buscar linea base
    line_base = ProyeccionAvanceObra.objects.filter(
        centro_costo=obra, es_base=True).order_by('-base_numero').first()

    # buscar avance_obra reales, y completar con la ultima revision
    avance_obra = AvanceObra.objects.filter(
        centro_costo=obra, periodo__fecha_fin__lt=periodo.fecha_fin)

    revision = ProyeccionAvanceObra.objects.filter(
        centro_costo=obra).order_by('-periodo__fecha_fin').first()

    # bucle por los periodos de la proyección

    periodo_range = ProyeccionAvanceObra.objects.filter(
        centro_costo=obra).aggregate(
            ini_fecha=Min('items__periodo__fecha_fin'),
            fin_fecha=Max('items__periodo__fecha_fin'))

    avance_obra_base = dict(line_base.items.values_list('periodo', 'avance'))
    avance_obra_real = dict([(avance.periodo_id, avance.avance) for avance in avance_obra])
    avance_obra_revision = dict(revision.items.values_list('periodo', 'avance'))

    data_real = []
    data_proy = []

    real_acumulado = 0
    proyectado_acumulado = 0
    is_first = True

    for periodo in Periodo.objects.filter(
            fecha_fin__gte=periodo_range["ini_fecha"],
            fecha_fin__lte=periodo_range["fin_fecha"]).order_by('fecha_fin'):
        if is_first:
            data_proy.append({'x': datetime_to_epoch(periodo.fecha_inicio), 'y': 0})
            data_real.append({'x': datetime_to_epoch(periodo.fecha_inicio), 'y': 0})
            is_first = False

        proyectado_acumulado += avance_obra_base.get(periodo.pk, 0)
        data_proy.append({'x': datetime_to_epoch(periodo.fecha_fin), 'y': proyectado_acumulado})

        real_acumulado += avance_obra_real.get(periodo.pk, avance_obra_revision.get(periodo.pk, 0))
        data_real.append({'x': datetime_to_epoch(periodo.fecha_fin), 'y': real_acumulado})

    return [
        {
            'key': "Avance Proyectado",
            'values': data_proy,
            'color': '#2ca02c',
            'strokeWidth': 2,
        },
        {
            'key': "Avance real",
            'values': data_real,
            'color': '#ff7f0e',
            'strokeWidth': 2,
        },
    ]


def get_consolidado_graph(obra, periodo):
    try:
        first_periodo = Periodo.objects.filter(fecha_inicio__lte=obra.fecha_inicio).latest("fecha_inicio")
        ultimo_dato_cert = Certificacion.objects.filter(obra=obra).latest('periodo__fecha_fin')
        ultimo_dato_costo = Costo.objects.filter(centro_costo=obra).latest('periodo__fecha_fin')
        ultima_fecha = obra.fecha_fin
        if not ultima_fecha:
            ultima_fecha = max(ultimo_dato_costo.periodo.fecha_fin, ultimo_dato_cert.periodo.fecha_fin)
    except ObjectDoesNotExist:
        raise ValueError("No pudo generarse el gráfico consolidado.")

    cert_real = dict(
        Certificacion.objects.filter(obra=obra).values(
            'periodo').annotate(total=Sum('items__monto')).values_list(
                'periodo', 'total').order_by('periodo__fecha_fin'))
    cert_proyeccion = dict(
        ProyeccionCertificacion.objects.filter(obra=obra).values(
            'periodo').annotate(total=Sum('items__monto')).values_list(
                'periodo', 'total').order_by('periodo__fecha_fin'))  #
    costo_real = dict(
        Costo.objects.filter(centro_costo=obra).values(
            'periodo').annotate(total=Sum('monto_total')).values_list(
                'periodo', 'total').order_by('periodo__fecha_fin'))  #
    costo_proy = dict(
        ProyeccionCosto.objects.filter(centro_costo=obra).values(
            'periodo').annotate(total=Sum('monto_total')).values_list(
                'periodo', 'total').order_by('periodo__fecha_fin'))  #

    data_cert_real = []
    data_cert_proy = []
    data_costo_real = []
    data_costo_proy = []
    data_revision_costos = []
    data_revision_venta = []

    data_cert_real_acumulado = 0
    data_cert_proy_acumulado = 0
    data_costo_real_acumulado = 0
    data_costo_proy_acumulado = 0
    presupuesto = Presupuesto.objects.filter(
        centro_costo=obra).latest('fecha')

    for periodo in Periodo.objects.filter(
            fecha_fin__gte=first_periodo.fecha_fin,
            fecha_fin__lte=ultima_fecha).order_by('fecha_fin'):
        fecha = datetime_to_epoch(periodo.fecha_fin)
        revision = presupuesto.revisiones.filter(fecha__lte=periodo.fecha_fin).latest('fecha')

        data_revision_costos.append({'x': fecha, 'y': revision.costo_industrial})
        data_revision_venta.append({'x': fecha, 'y': revision.total_venta})

        data_cert_real_acumulado += cert_real.get(periodo.pk, 0)
        data_cert_proy_acumulado += cert_proyeccion.get(periodo.pk, 0)
        data_costo_real_acumulado += costo_real.get(periodo.pk, 0)
        data_costo_proy_acumulado += costo_proy.get(periodo.pk, 0)

        data_cert_real.append({'x': fecha, 'y': data_cert_real_acumulado})
        data_cert_proy.append({'x': fecha, 'y': data_cert_proy_acumulado})
        data_costo_real.append({'x': fecha, 'y': data_costo_real_acumulado})
        data_costo_proy.append({'x': fecha, 'y': data_costo_proy_acumulado})

    return [
        {
            'key': "Cert. Real",
            'values': data_cert_real,
            'color': '#f47c3c',
            'strokeWidth': 2,
        },
        {
            'key': "Cert. Proyectada",
            'values': data_cert_proy,
            'color': '#ef5c0e',
            'strokeWidth': 2,
            'classed': 'dashed',
        },
        {
            'key': "Costos Reales",
            'values': data_costo_real,
            'color': '#93c54b',
            'strokeWidth': 2,
        },
        {
            'key': "Costos proyectados",
            'values': data_costo_proy,
            'color': '#79a736',
            'strokeWidth': 2,
            'classed': 'dashed',
        },
        {
            'key': "Costos Presupuestados",
            'values': data_revision_costos,
            'color': '#17759c',
            'strokeWidth': 2,
        },
        {
            'key': "Venta presupuestada",
            'values': data_revision_venta,
            'color': '#ff0470',
            'strokeWidth': 2,
        }
    ]
