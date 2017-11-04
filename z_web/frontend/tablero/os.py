# coding: utf-8
"""
Tablero de control para Obras de superficie.
"""
from decimal import Decimal as D
from django.db.models import Sum, F

from core.models import Obras
from organizacion.models import UnidadNegocio
from parametros.models import Periodo
from presupuestos.models import Presupuesto, Revision
from registro.models import CertificacionReal, CertificacionItem, CertificacionProyeccion
from costos.models import CostoReal, CostoProyeccion


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
        return self._2D(self.impuestos_y_contribuciones / self.subtotal_costo_industrial)

    @property
    def costo_financiero_e_imprevistos(self):
        return self._2D(self.revision.imprevistos_pesos +
                        self.revision.costo_financiero_pesos)

    @property
    def costo_financiero_e_imprevistos_perc(self):
        return self._2D(self.costo_financiero_e_imprevistos / self.subtotal_costo_industrial)

    @property
    def ganancias_despues_impuestos(self):
        return self._2D(self.revision.ganancias)

    @property
    def ganancias_despues_impuestos_perc(self):
        return self._2D(self.ganancias_despues_impuestos / self.subtotal_costo_industrial)

    @property
    def margen_bruto(self):
        return self._2D(
            self.costo_financiero_e_imprevistos + self.impuestos_y_contribuciones +
            self.ganancias_despues_impuestos)

    @property
    def margen_bruto_perc(self):
        return self._2D(self.margen_bruto / self.subtotal_costo_industrial)


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
                (self.revision.ingresos_brutos + self.revision.impuestos_cheque) * self.subtotal_venta
            ) + (self.ganancias_despues_impuestos * self.revision.impuestos_ganancias)
        )

    @property
    def costo_financiero_e_imprevistos(self):
        return self._2D(
            self.revision.imprevistos_pesos + (
                self.revision.costo_financiero_pesos * self.subtotal_costos_previstos))

    @property
    def ganancias_despues_impuestos(self):
        calc = self.subtotal_venta - (
            self.subtotal_costo_industrial + #I30
            self.costo_financiero_e_imprevistos +  #I33
            self.revision.sellado_pesos +  # $'Ppto. aprobado - R2'.I75
            ((self.revision.ingresos_brutos + self.revision.impuestos_cheque) * self.subtotal_venta)
        ) / (1 + self.revision.impuestos_ganancias)
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
            "comercial": self.presupuesto.to_dict()
        }

def generar_tablero(unidad_negocio, obra, periodo):

    presupuesto = Presupuesto.objects.filter(
        centro_costo=obra).latest('fecha')

    revision = presupuesto.revisiones.filter(fecha__lte=periodo.fecha_fin).latest('fecha')
    revision_b0 = presupuesto.revisiones.get(version=0)

    markup = MarkUp(revision, revision_b0)

    data_table = {}

    # acumulados
    venta = {}
    venta["acumulado"] = {
        "venta_contractual": CertificacionReal.objects.filter(
        obra=obra, items__adicional=False).aggregate(total=Sum('items__monto'))["total"] or 0,
        "ordenes_cambio": CertificacionReal.objects.filter(
        obra=obra, items__adicional=True).aggregate(total=Sum('items__monto'))["total"] or 0,
        "reajustes_precios": revision.reajustes_precio or 0,
        "reclamos_reconocidos": revision.reclamos_reconocidos or 0
    }
    venta["acumulado"]["subtotal"] = sum(venta["acumulado"].values())
    # en el futuro
    proyecciones_cert = CertificacionProyeccion.objects.filter(
        obra=obra, periodo__fecha_inicio__gt=periodo.fecha_fin)
    # faltante
    venta["faltante_estimado"] = {
        "venta_contractual": proyecciones_cert.filter(
            items__adicional=False).aggregate(total=Sum('items__monto'))["total"] or 0,
        "ordenes_cambio": proyecciones_cert.filter(
            items__adicional=True).aggregate(total=Sum('items__monto'))["total"] or 0,
        "reajustes_precios": 0,
        "reclamos_reconocidos": 0
    }
    venta["faltante_estimado"]["subtotal"] = sum(venta["faltante_estimado"].values())

    # faltante ppto
    venta["faltante_presupuesto"] = {
        "venta_contractual": revision.total_venta - venta["acumulado"]["venta_contractual"],
        "ordenes_cambio": revision.ordenes_cambio - venta["acumulado"]["ordenes_cambio"],
        "reajustes_precios": 0,  # revision.reajustes_precio - revision.reajustes_precio,
        "reclamos_reconocidos": 0  # revision.reclamos_reconocidos - revision.reclamos_reconocidos
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
    costos_reales = dict(CostoReal.objects.filter(
        centro_costo=obra).values('tipo_costo__nombre').annotate(
            total=Sum('monto_total')).values_list(
                'tipo_costo__nombre', 'total').order_by())
    costos_reales["subtotal"] = sum(costos_reales.values())

    # Faltante estimado son las proyecciones de costos
    costos_proyectados = dict(CostoProyeccion.objects.filter(
        centro_costo=obra, periodo__fecha_inicio__gt=periodo.fecha_fin).values(
            'tipo_costo__nombre').annotate(total=Sum('monto_total')).values_list(
                'tipo_costo__nombre', 'total').order_by())
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
    costos_faltante_presupuesto["subtotal"] = sum(costos_faltante_presupuesto.values())
    costos_total_estimado["subtotal"] = sum(costos_total_estimado.values())

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

    # No lo agrego aún porque falta los de estructura
    data_table["costos"] = costos

    # Estructura de Costos
    estructura_costos = {
        'presupuesto': {
            "contingencia": revision.contingencia,
            "estructura": revision.estructura_no_ree,
            "avales_gtia_seguros": (
                revision.aval_por_anticipos + revision.seguro_caucion + revision.seguro_5 +
                revision.aval_por_cumplimiento_contrato + revision.aval_por_cumplimiento_garantia
            )
        },
        "comercial": {
            "contingencia": revision_b0.contingencia,
            "estructura": revision_b0.estructura_no_ree,
            "avales_gtia_seguros": (
                revision_b0.aval_por_anticipos + revision_b0.seguro_caucion + revision_b0.seguro_5 +
                revision_b0.aval_por_cumplimiento_contrato + revision_b0.aval_por_cumplimiento_garantia
            )
        }
    }
    # estimado y presupuesto son iguales acá, pero no sus subtotales
    estructura_costos["estimado"] = estructura_costos["presupuesto"]

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

    return data_table
