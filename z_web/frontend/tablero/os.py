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
        """
        (valor de venta total ESTIMADO -
            {Costo industrial Estimado + Costo financiero e imprevistos Estimado + Sellado tomado del presupuesto VIGENTE + [
                (
                    valor porcentual de ingresos brutos según presupuesto VIGENTE +
                    valor porcentual de impuestos al cheque según presupuesto VIGENTE
                ) multiplicado por valor de venta total ESTIMADO
                ]
            }
        ) / (1 + valor porcentual de impuesto a las ganancias según presupuesto VIGENTE)
        """
        calc = (
            self.subtotal_venta - (
                self.subtotal_costo_industrial +
                self.costo_financiero_e_imprevistos +
                self.revision.sellado_pesos + (
                    (self.revision.ingresos_brutos + self.revision.impuestos_cheque) * self.subtotal_venta / 100)
                )
            )
        if calc >= 0:
            calc =  calc / (1 + (self.revision.impuestos_ganancias / 100))
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
        centro_costo=obra, aprobado=True).latest('fecha')

    try:
        revision = presupuesto.revisiones.filter(fecha__lte=periodo.fecha_fin).latest('fecha')
    except Revision.DoesNotExist:
        raise ValueError("No existen revisiones anteriores a la fecha "
                         "de fin del periodo ({0:%d-%m-%Y}".format(periodo.fecha_fin))
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
    ultima_revision = ProyeccionCertificacion.objects.filter(
        centro_costo=obra, periodo__fecha_fin__lte=periodo.fecha_fin).order_by(
            '-periodo__fecha_fin', 'es_base').first()

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
        "venta_contractual": ultima_revision.items.filter(
            periodo__fecha_fin__gt=periodo.fecha_fin).aggregate(total=Sum('monto'))["total"] or 0,
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

    # totales base 0
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
            '-periodo__fecha_fin', '-created_at').first()

    costos_proyectados = dict(proyeccion_costo_ultimo_ajuste.items.filter(
        periodo__fecha_fin__gt=periodo.fecha_fin).values(
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

    # Total comercial: busco el valor del items del presupuesto Base 0
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
    data_table["costos_keys"] = claves_costos

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

    # historico de revisiones
    data_table["revisiones_historico"] = []
    revisiones_historico = presupuesto.revisiones.filter(
        fecha__lte=periodo.fecha_fin).values(
            'version', 'fecha', 'valor_dolar').order_by('fecha')
    for rev in revisiones_historico:
        data_table["revisiones_historico"].append({
            'version': rev["version"],
            'fecha': rev["fecha"].strftime('%d/%m/%Y'),
            'valor_dolar': rev["valor_dolar"]
        })

    # guardo en cache esto por 30 segundos
    cache.set(key_cache, data_table, 30)
    return data_table


def datetime_to_epoch(date):
    # uso el primer día del mes como fecha del periodo, para que
    # los gráficos coincidan en la escala
    date = date.replace(day=1)
    return int(time.mktime(date.timetuple())) * 1000


def get_certificacion_data_2_graph(obra, periodo):
    # buscar linea base
    line_base = ProyeccionCertificacion.objects.filter(
        centro_costo=obra, es_base=True,
        periodo__fecha_fin__lte=periodo.fecha_fin).order_by('-base_numero').first()

    # buscar certificaciones reales, y completar con la ultima revision
    certificaciones = Certificacion.objects.filter(
        obra=obra, periodo__fecha_fin__lte=periodo.fecha_fin)

    revision = ProyeccionCertificacion.objects.filter(
        centro_costo=obra,
        periodo__fecha_fin__lte=periodo.fecha_fin).order_by(
            '-periodo__fecha_fin', 'es_base').first()

    return {
        'certificacion_base': dict(line_base.items.values_list('periodo', 'monto')),
        'certificacion_real': dict([(cert.periodo_id, cert.total) for cert in certificaciones]),
        'certificacion_proyeccion': dict(revision.items.values_list('periodo', 'monto')),
        'base_nombre': "Base {}".format(line_base.base_numero)
    }


def get_costos_data_2_graph(obra, periodo):
    # buscar linea base
    line_base = ProyeccionCosto.objects.filter(
        centro_costo=obra, es_base=True,
        periodo__fecha_fin__lte=periodo.fecha_fin).order_by('-base_numero').first()

    # buscar costos reales, y completar con la ultima revision
    costos = Costo.objects.filter(
        centro_costo=obra,
        periodo__fecha_fin__lte=periodo.fecha_fin).values('periodo').annotate(
            total=Sum('monto_total')).values_list('periodo', 'total')

    revision = ProyeccionCosto.objects.filter(
        centro_costo=obra,
        periodo__fecha_fin__lte=periodo.fecha_fin).order_by(
            '-periodo__fecha_fin', 'es_base').first()

    return {
        'costo_base': dict(
            line_base.items.values('periodo').annotate(
                total=Sum('monto')).values_list('periodo', 'total')
            ),
        'costo_real': dict(costos),
        'costo_proyeccion': dict(
            revision.items.values('periodo').annotate(
                total=Sum('monto')).values_list('periodo', 'total')
            ),
        'base_nombre': "Base {}".format(line_base.base_numero)
    }


def get_certificacion_graph(obra, periodo):

    # bucle por los periodos de la proyección
    periodo_range = ProyeccionCertificacion.objects.filter(
        centro_costo=obra).aggregate(
            ini_fecha=Min('items__periodo__fecha_fin'),
            fin_fecha=Max('items__periodo__fecha_fin'))

    data = get_certificacion_data_2_graph(obra, periodo)
    cert_base = data['certificacion_base']
    cert_real = data['certificacion_real']
    cert_revision = data['certificacion_proyeccion']

    data_real = []
    data_proy = []
    data_base = []

    for per in Periodo.objects.filter(
            fecha_fin__gte=periodo_range["ini_fecha"],
            fecha_fin__lte=periodo_range["fin_fecha"]).order_by('fecha_fin'):

        fecha = datetime_to_epoch(per.fecha_fin)
        # lo obtengo de la linea base
        data_base.append({
            'x': fecha,
            'y': cert_base.get(per.pk, 0)
        })
        if per.fecha_fin <= periodo.fecha_fin: # real
            # lo obtengo de la certificaciones
            data_real.append({
                'x': fecha,
                'y': cert_real.get(per.pk, 0)
            })
        else:  # proyección
            data_proy.append({
                'x': fecha,
                'y': cert_revision.get(per.pk, 0)
            })
    return [
        {
            'key': data["base_nombre"],
            'values': data_base,
            'color': '#4461fc'
        },
        {
            'key': "Cert. Real",
            'values': data_real,
            'color': '#ff7f0e'
        },
        {
            'key': "Cert. Ajustada",
            'values': data_proy,
            'color': '#2ca02c'
        },
    ]

def get_costos_graph(obra, periodo):

    # bucle por los periodos de la proyección
    periodo_range = ProyeccionCosto.objects.filter(
        centro_costo=obra).aggregate(
            ini_fecha=Min('items__periodo__fecha_fin'),
            fin_fecha=Max('items__periodo__fecha_fin'))

    data = get_costos_data_2_graph(obra, periodo)

    costo_base = data['costo_base']
    costo_real = data['costo_real']
    costo_revision = data['costo_proyeccion']

    data_real = []
    data_proy = []
    data_base = []

    for per in Periodo.objects.filter(
            fecha_fin__gte=periodo_range["ini_fecha"],
            fecha_fin__lte=periodo_range["fin_fecha"]).order_by('fecha_fin'):

        fecha = datetime_to_epoch(per.fecha_fin)
        # lo obtengo de la linea base
        data_base.append({
            'x': fecha,
            'y': costo_base.get(per.pk, 0)
        })
        if per.fecha_fin <= periodo.fecha_fin: # real
            # lo obtengo de costos
            data_real.append({
                'x': fecha,
                'y': costo_real.get(per.pk, 0)
            })
        else:  # proyección
            data_proy.append({
                'x': fecha,
                'y': costo_revision.get(per.pk, 0)
            })
    return [
        {
            'key': data['base_nombre'],
            'values': data_base,
            'color': '#4461fc'
        },
        {
            'key': "Costos reales",
            'values': data_real,
            'color': '#ff7f0e'
        },
        {
            'key': "Proyección de costos",
            'values': data_proy,
            'color': '#2ca02c'
        },
    ]


def get_avances_graph(obra, periodo):
    # buscar linea base
    line_base = ProyeccionAvanceObra.objects.filter(
        centro_costo=obra, es_base=True,
        periodo__fecha_fin__lte=periodo.fecha_fin).order_by('-base_numero').first()

    # buscar avance_obra reales, y completar con la ultima revision
    avance_obra = AvanceObra.objects.filter(
        centro_costo=obra, periodo__fecha_fin__lte=periodo.fecha_fin)

    revision = ProyeccionAvanceObra.objects.filter(
        centro_costo=obra,
        periodo__fecha_fin__lte=periodo.fecha_fin).order_by(
            '-periodo__fecha_fin', 'es_base').first()

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
    data_base = []

    base_acumulada = 0
    real_acumulado = 0
    proyectado_acumulado = 0
    is_first = True

    for per in Periodo.objects.filter(
            fecha_fin__gte=periodo_range["ini_fecha"],
            fecha_fin__lte=periodo_range["fin_fecha"]).order_by('fecha_fin'):


        if is_first:
            fecha_inicio = datetime_to_epoch(per.fecha_inicio)
            data_base.append({'x': fecha_inicio, 'y': 0})
            if per.fecha_fin <= periodo.fecha_fin:
                data_real.append({'x': fecha_inicio, 'y': 0})
            else:
                data_proy.append({'x': fecha_inicio, 'y': 0})
            is_first = False

        fecha = datetime_to_epoch(per.fecha_fin)
        base_acumulada += avance_obra_base.get(per.pk, 0)
        data_base.append({'x': fecha, 'y': base_acumulada})

        if per.fecha_fin < periodo.fecha_fin: # real
            real_acumulado += avance_obra_real.get(per.pk, 0)
            data_real.append({'x': fecha, 'y': real_acumulado})
        elif per.fecha_fin == periodo.fecha_fin:  # intersección
            real_acumulado += avance_obra_real.get(per.pk, 0)
            proyectado_acumulado = real_acumulado
            data_real.append({'x': fecha, 'y': real_acumulado})
            data_proy.append({'x': fecha, 'y': proyectado_acumulado})
        else:  # proyección
            proyectado_acumulado += avance_obra_revision.get(per.pk, 0)
            data_proy.append({'x': fecha, 'y': proyectado_acumulado})


    return [
        {
            'key': "Base {}".format(line_base.base_numero),
            'values': data_base,
            'color': '#4461fc',
            'strokeWidth': 1,
        },
        {
            'key': "Avance real",
            'values': data_real,
            'color': '#ff7f0e',
            'strokeWidth': 2,
        },
        {
            'key': "Avance Proyectado",
            'values': data_proy,
            'color': '#2ca02c',
            'classed': 'dashed',
            'strokeWidth': 2,
        },
    ]


def get_consolidado_graph(obra, periodo):

    # ventas
    data_ventas = get_certificacion_data_2_graph(obra, periodo)
    cert_base = data_ventas['certificacion_base']
    cert_real = data_ventas['certificacion_real']
    cert_revision = data_ventas['certificacion_proyeccion']

    # costos
    data_costos = get_costos_data_2_graph(obra, periodo)
    costo_base = data_costos['costo_base']
    costo_real = data_costos['costo_real']
    costo_revision = data_costos['costo_proyeccion']

    # bucle por los periodos de la proyección
    periodo_range = ProyeccionAvanceObra.objects.filter(
        centro_costo=obra).aggregate(
            ini_fecha=Min('items__periodo__fecha_fin'),
            fin_fecha=Max('items__periodo__fecha_fin'))

    data_real_ventas = []
    data_proy_ventas = []
    data_base_ventas = []

    data_real_costos = []
    data_proy_costos = []
    data_base_costos = []

    ventas_base_acumulado = 0
    ventas_real_acumulado = 0
    ventas_proy_acumulado = 0

    costos_base_acumulado = 0
    costos_real_acumulado = 0
    costos_proy_acumulado = 0

    is_first = True

    for per in Periodo.objects.filter(
            fecha_fin__gte=periodo_range["ini_fecha"],
            fecha_fin__lte=periodo_range["fin_fecha"]).order_by('fecha_fin'):

        fecha = datetime_to_epoch(per.fecha_fin)
        if is_first:
            fecha_inicio = datetime_to_epoch(per.fecha_inicio)
            data_base_ventas.append({'x': fecha_inicio, 'y': 0})
            data_base_costos.append({'x': fecha_inicio, 'y': 0})
            if per.fecha_fin <= periodo.fecha_fin:
                data_real_ventas.append({'x': fecha_inicio, 'y': 0})
                data_real_costos.append({'x': fecha_inicio, 'y': 0})
            else:
                data_proy_costos.append({'x': fecha_inicio, 'y': 0})
                data_proy_ventas.append({'x': fecha_inicio, 'y': 0})
            is_first = False

        # bases

        ventas_base_acumulado += cert_base.get(per.pk, 0)
        data_base_ventas.append({'x': fecha, 'y': ventas_base_acumulado})

        costos_base_acumulado += costo_base.get(per.pk, 0)
        data_base_costos.append({'x': fecha, 'y': costos_base_acumulado})

        if per.fecha_fin < periodo.fecha_fin: # real
            ventas_real_acumulado += cert_real.get(per.pk, 0)
            data_real_ventas.append({'x': fecha, 'y': ventas_real_acumulado})

            costos_real_acumulado += costo_real.get(per.pk, 0)
            data_real_costos.append({'x': fecha, 'y': costos_real_acumulado})

        elif per.fecha_fin == periodo.fecha_fin:  # intersección
            ventas_real_acumulado += cert_real.get(per.pk, 0)
            ventas_proy_acumulado = ventas_real_acumulado
            data_real_ventas.append({'x': fecha, 'y': ventas_real_acumulado})
            data_proy_ventas.append({'x': fecha, 'y': ventas_proy_acumulado})

            costos_real_acumulado += costo_real.get(per.pk, 0)
            costos_proy_acumulado = costos_real_acumulado
            data_real_costos.append({'x': fecha, 'y': costos_real_acumulado})
            data_proy_costos.append({'x': fecha, 'y': costos_proy_acumulado})

        else:
            ventas_proy_acumulado += cert_revision.get(per.pk, 0)
            data_proy_ventas.append({'x': fecha, 'y': ventas_proy_acumulado})
            costos_proy_acumulado += costo_revision.get(per.pk, 0)
            data_proy_costos.append({'x': fecha, 'y': costos_proy_acumulado})

    return [
        {
            'key': "Venta %s" % data_ventas["base_nombre"],
            'values': data_base_ventas,
            'color': '#4461fc',
            'strokeWidth': 1,
        },
        {
            'key': "Costos %s" % data_costos["base_nombre"],
            'values': data_base_costos,
            'color': '#ff1101',
            'strokeWidth': 1,
        },
        {
            'key': "Venta Real",
            'values': data_real_ventas,
            'color': '#79a736',
            'strokeWidth': 2,
        },
        {
            'key': "Venta proyectada",
            'values': data_proy_ventas,
            'color': 'rgb(0, 255, 128)',
            'strokeWidth': 2,
            'classed': 'dashed',
        },
        {
            'key': "Costos reales",
            'values': data_real_costos,
            'color': '#f47c3c',
            'strokeWidth': 2,
        },
        {
            'key': "Costos proyectados",
            'values': data_proy_costos,
            'color': 'rgb(255, 102, 0)',
            'strokeWidth': 2,
            'classed': 'dashed',
        }
    ]
