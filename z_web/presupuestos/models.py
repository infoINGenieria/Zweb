# coding: utf-8
from django.db import models

from simple_history.models import HistoricalRecords

from zweb_utils.models import BaseModelWithHistory, BaseModel
from core.models import Obras


class Presupuesto(BaseModel):
    """
    Un presupuesto para una obra.
    """
    centro_costo = models.ForeignKey(
        Obras, verbose_name='centro costo', related_name='presupuestos',
        limit_choices_to={'es_cc':True})
    fecha = models.DateField(verbose_name='fecha')
    aprobado = models.BooleanField(verbose_name='aprobado', default=False)

    class Meta:
        verbose_name = 'presupuesto'
        verbose_name_plural = 'presupuestos'

    def __str__(self):
        return "Presupuesto para {}".format(self.centro_costo)

    def save(self, *args, **kwargs):
        revision = None
        if not self.pk:
            revision = Revision(version=0, fecha=self.fecha, valor_dolar=0)
        super(Presupuesto, self).save(*args, **kwargs)
        if revision:
            revision.presupuesto = self
            revision.save()

    @property
    def fecha_vigente(self):
        if self.revision_vigente:
            return self.revision_vigente.fecha
        return None

    @property
    def revision_vigente(self):
        return self.revisiones.latest('version')

    @property
    def venta_actual(self):
        return self.revision_vigente.total_venta

    @property
    def venta_revision_anterior(self):
        if self.revision_vigente.version == 0:
            return 0
        anterior = self.revisiones.get(version=self.revision_vigente.version - 1)
        return anterior.total_venta

    @property
    def versiones(self):
        return self.revisiones.values_list('version', flat=True).order_by('-version')


class TipoItemPresupuesto(BaseModel):
    """
    Un tipo de item del presupuesto.
    """
    nombre = models.CharField(verbose_name='nombre', max_length=255, unique=True)

    class Meta:
        verbose_name = 'tipo de ítem de presupuesto'
        verbose_name_plural = 'tipos de ítem de presupuesto'

    def __str__(self):
        return self.nombre


class Revision(BaseModelWithHistory):
    """
    Una versión de un presupuesto.
    """
    presupuesto = models.ForeignKey(
        Presupuesto, verbose_name='presupuesto', related_name='revisiones')

    version = models.PositiveIntegerField(verbose_name='version')
    fecha = models.DateField(verbose_name='fecha')
    valor_dolar = models.DecimalField(verbose_name='valor dolar', decimal_places=2, max_digits=18)

    history = HistoricalRecords()

    # Campos basados en el excel
    venta_contractual_b0 = models.DecimalField(
        verbose_name='venta contractual base cero',
        decimal_places=2, max_digits=18, null=True)
    ordenes_cambio = models.DecimalField(
        verbose_name='órdenes de cambio',
        decimal_places=2, max_digits=18, null=True)
    reajustes_precio = models.DecimalField(
        verbose_name='reajustes de precio',
        decimal_places=2, max_digits=18, null=True)
    reclamos_reconocidos = models.DecimalField(
        verbose_name='reclamos reconocidos',
        decimal_places=2, max_digits=18, null=True)

    ## Estructura de costos generales
    contingencia = models.DecimalField(
        verbose_name='contingencia', decimal_places=2, max_digits=18,
        help_text="Sobre costos previstos", null=True)

    estructura_no_ree = models.DecimalField(
        verbose_name='estructura no contemplada en REE', decimal_places=2, max_digits=18,
        help_text="Sobre costos previstos", null=True)

    aval_por_anticipos = models.DecimalField(
        verbose_name='aval por anticipos', decimal_places=2, max_digits=18,
        help_text="Sobre porcentaje de la venta", null=True)

    seguro_caucion = models.DecimalField(
        verbose_name='seguro de caución', decimal_places=2, max_digits=18,
        help_text="Sobre venta", null=True)

    aval_por_cumplimiento_contrato = models.DecimalField(
        verbose_name='aval por cumplimiento de contrato', decimal_places=2, max_digits=18,
        help_text="Sobre venta", null=True)

    aval_por_cumplimiento_garantia = models.DecimalField(
        verbose_name='aval por cumplimiento de garantia', decimal_places=2, max_digits=18,
        help_text="Sobre venta", null=True)

    seguro_5 = models.DecimalField(
        verbose_name='seguro_5', decimal_places=2, max_digits=18,
        help_text="Sobre venta", null=True)

    ## Mark up
    imprevistos = models.DecimalField(
        verbose_name='imprevistos', decimal_places=2, max_digits=18,
        help_text="Sobre costo industrial", null=True)

    ganancias = models.DecimalField(
        verbose_name='ganancias', decimal_places=2, max_digits=18,
        help_text="Sobre costo industrial", null=True)

    impuestos_ganancias = models.DecimalField(
        verbose_name='impuestos ganancias', decimal_places=2, max_digits=18,
        help_text="Sobre Ganancia Neta", null=True)

    sellado = models.DecimalField(
        verbose_name='sellado', decimal_places=2, max_digits=18,
        help_text="Sobre Venta", null=True)

    ingresos_brutos = models.DecimalField(
        verbose_name='ingresos brutos', decimal_places=2, max_digits=18,
        help_text="Sobre Venta", null=True)

    impuestos_cheque = models.DecimalField(
        verbose_name='impuestos al cheque', decimal_places=2, max_digits=18,
        help_text="Sobre Venta", null=True)

    costo_financiero = models.DecimalField(
        verbose_name='costo financiero', decimal_places=2, max_digits=18,
        help_text="Sobre Costo industrial", null=True)

    class Meta:
        verbose_name = 'revision'
        verbose_name_plural = 'revisiones'
        unique_together = ('presupuesto', 'version')

    def __str__(self):
        return "Revisión {} ({})".format(self.version, self.presupuesto)

    @property
    def total_venta(self):
        total = self.venta_contractual_b0 if self.venta_contractual_b0 else 0
        total += self.ordenes_cambio if self.ordenes_cambio else 0
        total += self.reajustes_precio if self.reajustes_precio else 0
        total += self.reclamos_reconocidos if self.reclamos_reconocidos else 0
        return total


class ItemPresupuesto(BaseModelWithHistory):
    """
    Un ítem del presupuesto.
    """
    revision = models.ForeignKey(
        Revision, verbose_name='revision', related_name='items')
    tipo = models.ForeignKey(
        TipoItemPresupuesto, verbose_name='tipo de item', related_name='valores')
    pesos = models.DecimalField(verbose_name='$', decimal_places=2, max_digits=18)
    dolares = models.DecimalField(verbose_name='USD', decimal_places=2, max_digits=18)
    observaciones = models.TextField(verbose_name='observaciones', null=True, blank=True)
    indirecto = models.BooleanField(verbose_name='indirecto', default=False)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'ítem de presupuesto'
        verbose_name_plural = 'ítemes de presupuesto'

    def __str__(self):
        _str = "{} - ${}".format(self.tipo, self.pesos)
        if self.dolares:
            _str = "{} - USD{}".format(_str, self.dolares)
        return _str
