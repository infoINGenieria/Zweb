# coding: utf-8
from decimal import Decimal as D

from django.db import models
from django.core.exceptions import FieldError

from simple_history.models import HistoricalRecords

from parametros.models import Periodo
from core.models import Equipos, Obras
from zweb_utils.models import BaseModel

from .managers import ValoresManager


class ValoresMixin(object):
    model_parametros = None

    @property
    def mis_parametros(self):
        if hasattr(self, '_mis_parametros') and self._mis_parametros is not None:
            return self._mis_parametros
        self._mis_parametros = self.get_dato_vigente(self.model_parametros)
        return self._mis_parametros

    def get_dato_vigente(self, model):
        """
        busca los valores del tipo de modelo dado válido para el periodo correspondiente.
        """
        try:
            return model.objects.filter(
                equipo=self.equipo,
                valido_desde__fecha_inicio__lte=self.valido_desde.fecha_inicio
                ).order_by('-valido_desde__fecha_inicio').first()
        except FieldError:
            return model.objects.filter(
                valido_desde__fecha_inicio__lte=self.valido_desde.fecha_inicio
                ).order_by('-valido_desde__fecha_inicio').first()


class BaseParametrosCostos(BaseModel):
    class Meta:
        abstract = True

    equipo = models.ForeignKey(Equipos, verbose_name='equipo')
    valido_desde = models.ForeignKey(Periodo, verbose_name="válido desde")

    @property
    def parametros_gral(self):
        if not hasattr(self, '_vigente'):
            self._vigente = ParametrosGenerales.vigente(self.valido_desde)
        return self._vigente


class ParametrosGenerales(BaseModel):
    valido_desde = models.OneToOneField(Periodo, verbose_name="válido desde")
    consumo_equipo_viales = models.DecimalField(
        'consumo específico equipos viales (l/h/HP)',
        decimal_places=3, max_digits=5)
    consumo_equipo_automotor = models.DecimalField(
        'consumo específico equipos automotor (l/h/HP)',
        decimal_places=3, max_digits=5)
    precio_gasoil = models.DecimalField(
        'precio GO ($/l a granel sin impuestos deducibles)',
        decimal_places=3, max_digits=18)
    precio_lubricante = models.DecimalField(
        'precio lubricante $/l (a granel sin impuestos deducibles)',
        decimal_places=3, max_digits=18)
    precio_hidraulico = models.DecimalField(
        'precio fluido hidráulico (a granel sin impuestos deducibles)',
        decimal_places=3, max_digits=18)
    horas_por_dia = models.IntegerField('horas por día', default=6)
    dias_por_mes = models.IntegerField('días por mes', default=21)
    horas_trabajo_anio = models.IntegerField(
        'horas trabajo por año', default=1584)
    valor_dolar = models.DecimalField(
        'USD/$', decimal_places=3, max_digits=18)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'parámetro general de taller'
        verbose_name_plural = 'parámetros generales de taller'

    def __str__(self):
        return "parámetro de taller (%s)" % self.valido_desde

    @classmethod
    def vigente(cls, periodo):
        return ParametrosGenerales.objects.filter(
            valido_desde__fecha_inicio__lte=periodo.fecha_inicio
        ).order_by('-valido_desde__fecha_inicio').first()


class LubricantesParametros(BaseParametrosCostos):
    """
    Se configura los parámetros para el calculo del costo
    de los lubricantes, fluidos hidráulicos y filtros de un equipo,
    a partir de un periodo dado.
    """
    hp = models.DecimalField('HP', max_digits=18, decimal_places=2, null=True)

    class Meta:
        verbose_name = 'parámetro de lubricante'
        verbose_name_plural = 'parámetros de lubricantes'


class LubricanteItem(BaseModel):
    descripcion = models.CharField('descripción del ítem', max_length=255)
    es_filtro = models.BooleanField(
        'El item es un filtro?', default=True,
        help_text='Seleccionar para filtros, no seleccionar para lubricantes o fluidos hidráulicos')
    observaciones = models.TextField('observaciones', blank=True, null=True)

    class Meta:
        verbose_name = 'ítem de lubricantes / hidráulicos / filtros'
        verbose_name_plural = 'ítemes de lubricantes / hidráulicos / filtros'

    def __str__(self):
        return self.descripcion


class LubricantesParametrosItem(BaseModel):
    parametro = models.ForeignKey(LubricantesParametros, related_name='items_lubricante')
    item = models.ForeignKey(LubricanteItem, related_name='parametros')
    cambios_por_anio = models.DecimalField(
        'cambios por año', max_digits=5,
        decimal_places=2, default=0)
    volumen_por_cambio = models.DecimalField(
        'volumen (L) por cambio',
        max_digits=5, decimal_places=2, default=1)

    class Meta:
        verbose_name = 'ítem de parámetros de lubricantes / hidráulicos /filtros'
        verbose_name_plural = 'ítemes de parámetros de lubricantes / hidráulicos / filtros'


class LubricantesValores(ValoresMixin, BaseParametrosCostos):
    """
    Valores de los filtros por equipo, vigente desde un periodo dado.
    """

    history = HistoricalRecords()

    model_parametros = LubricantesParametros

    objects = ValoresManager()

    class Meta:
        verbose_name = 'valor de lubricantes / hidráulicos / filtros'
        verbose_name_plural = 'valores de lubricantes / hidráulicos / filtros'

    @property
    def costo_total_pesos_hora(self):
        param = self.parametros_gral
        if param:
            return self.costo_total_pesos_mes / param.dias_por_mes / param.horas_por_dia
        return D(0)

    @property
    def costo_total_pesos_mes(self):
        item_valores = self.valores.aggregate(total=models.Sum('costo_por_mes')).get('total')
        return item_valores


class LubricantesValoresItem(ValoresMixin, BaseModel):
    valor = models.ForeignKey(LubricantesValores, related_name='valores')
    item = models.ForeignKey(LubricanteItem, related_name='itemes')
    valor_unitario = models.DecimalField(
        'valor unitario', max_digits=18, decimal_places=2, default=0,
        help_text='Precio por unidad o litro.')

    costo_por_mes = models.DecimalField(
        'costo ($/m)', max_digits=18, decimal_places=2, blank=True,
        help_text='No completar, se calculará automáticamente.'
    )
    class Meta:
        verbose_name = 'ítem de valores de lubricantes / hidráulicos /filtros'
        verbose_name_plural = 'ítemes de valores de lubricantes / hidráulicos / filtros'

    def calcular(self):
        parametro = self.valor.mis_parametros
        if not parametro:
            return D(0)
        item = parametro.items_lubricante.filter(item=self.item).first()
        if not item:
            return D(0)
        costo = self.valor_unitario * item.cambios_por_anio
        if not item.item.es_filtro:
            costo *= item.volumen_por_cambio
        return costo / 12

    def save(self, *args, **kwargs):
        self.costo_por_mes = self.calcular()
        super(LubricantesValoresItem, self).save(*args, **kwargs)


class TrenRodajeParametros(BaseParametrosCostos):
    # neumáticos
    vida_util_neumatico = models.IntegerField('vida util estimada (h)', null=True, blank=True)
    cantidad_neumaticos = models.IntegerField('neumáticos por equipo', null=True, blank=True)
    medidas = models.CharField('medidas', max_length=24, null=True, blank=True)

    # orugas
    factor_basico = models.DecimalField('factor básico', max_digits=5, decimal_places=2, null=True, blank=True)
    impacto = models.DecimalField('impacto', max_digits=5, decimal_places=2, null=True, blank=True)
    abracion = models.DecimalField('abración', max_digits=5, decimal_places=2, null=True, blank=True)
    z = models.DecimalField('z', max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'parámetro de tren de rodaje'
        verbose_name_plural = 'parámetros de tren de rodaje'


    @property
    def orugas_costo_USD_hora(self):
        try:
            return self.z * (self.factor_basico + self.impacto + self.abracion)
        except TypeError:
            return D(0)

    @property
    def neumaticos_cambios_por_anio(self):
        param = self.parametros_gral
        if param and self.vida_util_neumatico:
            return param.horas_trabajo_anio / D(self.vida_util_neumatico)
        return D(0)


class TrenRodajeValores(ValoresMixin, BaseParametrosCostos):
    # Neumáticos
    precio_neumatico = models.DecimalField('CU Neumático', max_digits=18, decimal_places=3)

    # Orugas
    # NO HAY VALORES CAMBIANTES MAS QUE EL DOLAR

    history = HistoricalRecords()

    model_parametros = TrenRodajeParametros
    objects = ValoresManager()

    class Meta:
        verbose_name = 'valor de tren de rodaje'
        verbose_name_plural = 'valores de tren de rodaje'

    @property
    def costo_neumaticos_pesos_hora(self):
        param = self.parametros_gral
        if param and self.mis_parametros:
            try:
                costo = (
                    self.precio_neumatico * self.mis_parametros.cantidad_neumaticos *
                    self.mis_parametros.neumaticos_cambios_por_anio
                    ) / param.horas_trabajo_anio
                return costo
            except TypeError:
                pass
        return D(0)

    @property
    def costo_neumaticos_pesos_mes(self):
        if self.parametros_gral:
            return self.parametros_gral.horas_trabajo_anio * self.costo_neumaticos_pesos_hora / 12
        return D(0)

    @property
    def costo_orugas_pesos_hora(self):
        if self.parametros_gral and self.mis_parametros:
            return self.parametros_gral.valor_dolar * self.mis_parametros.orugas_costo_USD_hora
        return D(0)

    @property
    def costo_orugas_pesos_mes(self):
        if self.parametros_gral:
            return self.parametros_gral.horas_trabajo_anio * self.costo_orugas_pesos_hora / 12
        return D(0)

    @property
    def costo_total_pesos_hora(self):
        return self.costo_neumaticos_pesos_hora + self.costo_orugas_pesos_hora

    @property
    def costo_total_pesos_mes(self):
        return self.costo_neumaticos_pesos_mes + self.costo_orugas_pesos_mes


class PosesionParametros(BaseParametrosCostos):
    posesion_hs = models.IntegerField('periodo de posesion (h)')
    precio_del_activo = models.DecimalField('precio del activo (USD)', max_digits=18, decimal_places=2)
    residual = models.DecimalField('residual', max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = 'parámetro de posesión'
        verbose_name_plural = 'parámetros de posesion'

    @property
    def posesion_en_anios(self):
        if self.parametros_gral:
            return D(self.posesion_hs) / self.parametros_gral.horas_trabajo_anio
        return D(0)

    @property
    def residual_en_USD(self):
        return self.residual * self.precio_del_activo


class PosesionValores(ValoresMixin, BaseParametrosCostos):
    #SEGUROS
    seguros = models.DecimalField('seguros', max_digits=18, decimal_places=2, help_text='$/mes')
    #R.U.T.A
    ruta = models.DecimalField('R.U.T.A', max_digits=18, decimal_places=2, help_text='$/mes')
    #VTV
    vtv = models.DecimalField('VTV', max_digits=18, decimal_places=2, help_text='$/mes')
    #CERTIFICACION (IRAM)
    certificacion = models.DecimalField('certificacion (IRAM)', max_digits=18, decimal_places=2, help_text='$/mes')
    #HABILITACIONES
    habilitaciones= models.DecimalField('habilitaciones', max_digits=18, decimal_places=2, help_text='$/mes')
    #RSV
    rsv = models.DecimalField('RSV', max_digits=18, decimal_places=2, help_text='$/mes')
    #VHF
    vhf = models.DecimalField('VHF', max_digits=18, decimal_places=2, help_text='$/mes')
    #IMPUESTOS
    impuestos = models.DecimalField('impuestos', max_digits=18, decimal_places=2, help_text='$/mes')

    history = HistoricalRecords()

    model_parametros = PosesionParametros
    objects = ValoresManager()

    class Meta:
        verbose_name = 'valor de posesión'
        verbose_name_plural = 'valores de posesión'

    @property
    def costo_anual(self):
        valor_dolar = self.parametros_gral.valor_dolar if self.parametros_gral else 0
        if self.mis_parametros:
            #=+(L6-N6)*$F$170/K6+(O6++P6+Q6+R6+S6+T6+U6+V6)*12
            costo = (
                (self.mis_parametros.precio_del_activo - self.mis_parametros.residual_en_USD) * valor_dolar / self.mis_parametros.posesion_en_anios
            ) + (self.seguros + self.ruta + self.vtv + self.certificacion +
                 self.habilitaciones + self.rsv + self.vhf + self.impuestos) * 12
            return costo
        return D(0)

    @property
    def costo_total_pesos_mes(self):
        return self.costo_anual / 12

    @property
    def costo_total_pesos_hora(self):
        if self.parametros_gral:
            return self.costo_anual / self.parametros_gral.horas_trabajo_anio
        return D(0)


class ReparacionesParametros(BaseParametrosCostos):
    factor_basico = models.DecimalField('factor básico de reparación', max_digits=18, decimal_places=2)
    multiplicador = models.DecimalField('multiplicador de duración prolongada', max_digits=18, decimal_places=2)

    class Meta:
        verbose_name = 'parámetro de reparación'
        verbose_name_plural = 'parámetros de reparaciones'


class ReparacionesValores(ValoresMixin, BaseParametrosCostos):

    # NO HAY VALORES CAMBIANTES
    history = HistoricalRecords()

    model_parametros = ReparacionesParametros
    objects = ValoresManager()

    class Meta:
        verbose_name = 'valor de reparación'
        verbose_name_plural = 'valores de reparaciones'

    @property
    def costo_total_pesos_hora(self):
        if self.parametros_gral and self.mis_parametros:
            return self.mis_parametros.factor_basico * self.mis_parametros.multiplicador * self.parametros_gral.valor_dolar
        return D(0)

    @property
    def costo_total_pesos_mes(self):
        if self.parametros_gral:
            return self.costo_total_pesos_hora * self.parametros_gral.horas_trabajo_anio / 12
        return D(0)


class ManoObraValores(BaseModel):
    valido_desde = models.OneToOneField(Periodo, verbose_name="válido desde")
    taller = models.DecimalField('taller', max_digits=18, decimal_places=2)
    plataforma_combustible = models.DecimalField('plataforma de combustible', max_digits=18, decimal_places=2)
    carretones = models.DecimalField('carretones', max_digits=18, decimal_places=2)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'valor de mano de obra'
        verbose_name_plural = 'valores de mano de obra'


class EquipoAlquiladoValores(BaseParametrosCostos):
    alquiler = models.DecimalField('Desgastables + mano de obra + etc', decimal_places=2, max_digits=18)

    history = HistoricalRecords()
    objects = ValoresManager()

    class Meta:
        verbose_name = 'valor de equipo alquilado'
        verbose_name_plural = 'valores de equipos alquilados'


class CostoEquipoValores(ValoresMixin, BaseParametrosCostos):
    markup = models.DecimalField('Mark Up (%)', decimal_places=2, max_digits=18)

    # campos calculados guardados para facilidad de creación de informes
    costo_mensual_del_activo_calculado = models.DecimalField(
        'Costo mensual del activo', decimal_places=2, max_digits=18, default=0)
    costo_mensual_del_activo_con_mo_calculado = models.DecimalField(
        'Costo mensual del activo con Mano de obra',
        decimal_places=2, max_digits=18, default=0)
    costo_equipo_calculado = models.DecimalField(
        'Costo equipo', decimal_places=2, max_digits=18, default=0)

    history = HistoricalRecords()
    objects = ValoresManager()
    """
    EQUIPO PROPIO

    costos_lubri_hidraulicos = costo_pesos_mes
    costos_tren_rodaje = costo_pesos_mes
    costos_posesion = costo_pesos_mes
    costos_reparaciones = costo_pesos_mes

    costo_mensual_del_activo = costos_lubri_hidraulicos + costos_tren_rodaje + costos_posesion + costos_reparaciones  # sin mano de obra

    total_flota = SUM(costo_mensual_del_activo de cada equipo propio)
    costo_mensual_del_activo_con_mo = (costo_mensual_del_activo * ManoObraValores.taller) / total_flota

    COSTO_ALQUILER_ZILLE = (costo_mensual_del_activo + costo_mensual_del_activo_con_mo) * markup / 100

    EQUIPO ALQUILADO

    ¡¡No hay ejemplos!!

    COSTO_ALQUILER_ZILLE = EquipoAlquiladoValores

    """

    @property
    def costo_mensual_del_activo(self):
        if self.equipo.es_alquilado:
            return D(0)
        # lubricantes, hidraulicos y filtros
        costos_lubri_hidraulicos = self._costo_mensual(self.get_dato_vigente(LubricantesValores))
        # tren de rodaje
        costos_tren_rodaje = self._costo_mensual(self.get_dato_vigente(TrenRodajeValores))
        # Posesión
        costos_posesion = self._costo_mensual(self.get_dato_vigente(PosesionValores))
        # Reserva para reparaciones
        costos_reparaciones = self._costo_mensual(self.get_dato_vigente(ReparacionesValores))

        costo_mensual_del_activo = costos_lubri_hidraulicos + costos_tren_rodaje + costos_posesion + costos_reparaciones  # sin mano de obra
        # almaceno siempre después de calcular
        self.costo_mensual_del_activo_calculado = costo_mensual_del_activo
        self.save()
        return costo_mensual_del_activo


    def _costo_mensual(self, parametros):
        if parametros:
            return parametros.costo_total_pesos_mes
        else:
            return D(0)

    @property
    def costo_mensual_mo_logistico(self):
        # costo de mano de obra logistico (Carretones)
        mo_log = 0
        if self.equipo.implica_mo_logistica:
            mo_valor = self.get_dato_vigente(ManoObraValores)
            if mo_valor:
                count = Equipos.objects.filter(implica_mo_logistica=True).count()
                mo_log = mo_valor.carretones / count
        return mo_log

    @property
    def costo_equipo_propio(self):
        if self.equipo.es_alquilado:
            return D(0)
        self.costo_equipo_calculado = (
            self.costo_mensual_del_activo +
            self.costo_mensual_del_activo_con_mo +
            self.costo_mensual_mo_logistico
            ) * self.markup / 100
        self.save()
        return self.costo_equipo_calculado

    @property
    def costo_mensual_del_activo_con_mo(self):
        # costo_mensual_del_activo_con_mo = (costo_mensual_del_activo * ManoObraValores.taller) / total_flota
        mo_valor =self.get_dato_vigente(ManoObraValores)
        total_flota = self.get_dato_vigente(TotalFlota)
        if mo_valor and total_flota and total_flota.monto:
            taller = mo_valor.taller
            self.costo_mensual_del_activo_con_mo_calculado = (self.costo_mensual_del_activo * taller) / total_flota.monto
        else:
            self.costo_mensual_del_activo_con_mo_calculado = 0
        self.save()
        return self.costo_mensual_del_activo_con_mo_calculado

    @property
    def costo_equipo_alquilado(self):
        if not self.equipo.es_alquilado:
            return D(0)
        equipo_alquilado = self.get_dato_vigente(EquipoAlquiladoValores)
        if equipo_alquilado:
            self.costo_equipo_calculado = equipo_alquilado.alquiler
        else:
            self.costo_equipo_calculado = 0
        self.save()
        return self.costo_equipo_calculado

    @property
    def costo_mensual_zille(self):
        if self.equipo.es_alquilado:
            return self.costo_equipo_alquilado
        return self.costo_equipo_propio

    def calcular(self):
        return self.costo_mensual_zille

    class Meta:
        verbose_name = 'valor de costo equipo'
        verbose_name_plural = 'valores de costo de equipo'


class TotalFlota(BaseModel):
    valido_desde = models.OneToOneField(Periodo, verbose_name="válido desde")
    monto = models.DecimalField('Total Flota($)', decimal_places=2, max_digits=18, default=0)
    cantidad = models.IntegerField('Cantidad equipos', default=0)

    def calcular_total_flota(self):
        """
        Recalcular todos los valores válidos para el periodo correspondiente.
        """
        monto_aux = 0
        cantidad_aux = 0
        for equipo in Equipos.objects.actives_as_of(self.valido_desde.fecha_inicio):
            valor = CostoEquipoValores.objects.vigente(
                equipo=equipo, periodo=self.valido_desde)
            if valor:
                # llamamos al property para recalcular costos
                aux = valor.costo_mensual_zille
                monto_aux += valor.costo_mensual_del_activo
                cantidad_aux += 1
        self.monto = monto_aux
        self.cantidad = cantidad_aux
        self.save()
        return self.monto


class AsistenciaEquipo(BaseModel):
    """
    Representa la asistencia de equipos un día dado.
    """
    dia = models.DateField(verbose_name='día', unique=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'dia de asistencia de equipo a cc'
        verbose_name_plural = 'dias de asistencias de equipo a cc'

    def __str__(self):
        return self.dia.strftime("%d/%m/%Y")


class RegistroAsistenciaEquipo(BaseModel):
    """
    Representa la asistencia de un equipo a una obra un día dado.
    """
    asistencia = models.ForeignKey(AsistenciaEquipo, verbose_name='dia de asistencia',
                                   related_name='registros')
    equipo = models.ForeignKey(Equipos, verbose_name='equipo')
    centro_costo = models.ForeignKey(Obras, verbose_name='centro de costo',
                                     limit_choices_to={'es_cc':True})

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'registro de asistencia de equipo a cc'
        verbose_name_plural = 'registros de asistencias de equipo a cc'
        unique_together = ('asistencia', 'equipo', 'centro_costo')

    def __str__(self):
        return "{} en {}".format(self.equipo, self.centro_costo)
