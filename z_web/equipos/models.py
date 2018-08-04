from django.db import models

from simple_history.models import HistoricalRecords

from parametros.models import Periodo
from core.models import Equipos, Obras
from zweb_utils.models import BaseModel


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
            valido_desde__fecha_inicio__lte=periodo.valido_desde__fecha_inicio
        ).order_by('-valido_desde__fecha_inicio').first()

class LubricantesParametros(BaseParametrosCostos):
    """
    Se configura los parámetros para el calculo del costo
    de los lubricantes, fluidos hidráulicos y filtros de un equipo,
    a partir de un periodo dado.
    """
    hp = models.DecimalField('HP', max_digits=18, decimal_places=2, null=True)

    # lubricantes
    consumo_medio = models.DecimalField(
        'consumo medio (l/h)', max_digits=18,
        decimal_places=3, null=True)
    cambios_lubricante_en_2000 = models.DecimalField(
        'cambios de lubricante en 2000h', max_digits=5,
        decimal_places=2, null=True)
    volumen_lubricante_por_cambio = models.DecimalField(
        'volumen (L) de lubricante por cambio',
        max_digits=5, decimal_places=2, null=True)

    # hidraulico
    volumen_hidraulico_por_cambio = models.DecimalField(
        'volumen (L) hidráulico por cambio',
        max_digits=5, decimal_places=2, null=True
    )

    class Meta:
        verbose_name = 'parámetro de lubricante'
        verbose_name_plural = 'parámetros de lubricantes'

    @property
    def cambios_lubricante_por_anio(self):
        param = self.parametros_gral
        if param:
            return self.cambios_lubricante_en_2000 / 2000 * param.horas_trabajo_anio

    @property
    def cambios_hidraulico_por_anio(self):
        lubr = self.cambios_lubricante_por_anio
        if lubr:
            return lubr / 2

    @property
    def lubricante_costo_pesos_hora(self):
        param = self.parametros_gral
        if param:
            costo = (self.consumo_medio * param.precio_lubricante) + (
                self.cambios_lubricante_por_anio * self.volumen_lubricante_por_cambio *
                param.precio_lubricante / param.horas_trabajo_anio
            )
            return costo
        return 0

    @property
    def hidraulico_costo_pesos_hora(self):
        param = self.parametros_gral
        if param:
            costo = (self.volumen_hidraulico_por_cambio * self.cambios_hidraulico_por_anio *
                    param.precio_hidraulico / param.horas_trabajo_anio)
            return costo
        return 0

    # FILTROS
    @property
    def cambio_filtro_aire(self):
        """
        Igual a los cambios de lubricante
        """
        return self.cambios_lubricante_por_anio

    @property
    def costo_filtro_aire_pesos_anio(self):
        costo_unitario = self.costo_unitario_filtro('aire')
        return costo_unitario * self.cambio_filtro_aire

    @property
    def cambio_filtro_combustible(self):
        """
        Igual a los cambios de lubricante
        """
        return self.cambios_lubricante_por_anio

    @property
    def costo_filtro_combustible_pesos_anio(self):
        costo_unitario = self.costo_unitario_filtro('combustible')
        return costo_unitario * self.cambio_filtro_combustible

    @property
    def cambio_filtro_hidraulico(self):
        """
        Igual a los cambios de hidraulico
        """
        return self.cambios_hidraulico_por_anio

    @property
    def costo_filtro_hidraulico_pesos_anio(self):
        costo_unitario = self.costo_unitario_filtro('hidraulico')
        return costo_unitario * self.cambio_filtro_hidraulico

    @property
    def cambio_filtro_lubricante(self):
        """
        Igual a los cambios de lubricante
        """
        return self.cambios_lubricante_por_anio

    @property
    def costo_filtro_lubricante_pesos_anio(self):
        costo_unitario = self.costo_unitario_filtro('lubricante')
        return costo_unitario * self.cambio_filtro_lubricante

    @property
    def filtro_costo_pesos_hora(self):
        param = self.parametros_gral
        if param:
            costo = self.costo_filtro_aire_pesos_anio
            costo += self.costo_filtro_combustible_pesos_anio
            costo += self.costo_filtro_hidraulico_pesos_anio
            costo += self.costo_filtro_lubricante_pesos_anio
            costo = costo / param.horas_trabajo_anio
            return costo
        return 0

    @property
    def costo_total_pesos_hora(self):
        return (
            self.lubricante_costo_pesos_hora +
            self.hidraulico_costo_pesos_hora +
            self.filtro_costo_pesos_hora)

    @property
    def costo_total_pesos_mes(self):
        param = self.parametros_gral
        if param:
            return self.costo_total_pesos_hora * param.horas_trabajo_anio / 12
        return 0

    def costo_unitario_filtro(self, filtro):
        if not hasattr(self, '_valor') or self._valor is None:
            # encontrar el precio del filtro para el periodo dado
            self._valor = LubricantesValores.objects.filter(
                equipo=self.equipo,
                periodo__fecha_inicio__lte=self.periodo.fecha_inicio
                ).order_by('-periodo__fecha_inicio').first()
        if self._valor:
            return getattr(self._valor, "precio_filtro_%s" % filtro, 0)
        return 0


class LubricantesValores(BaseParametrosCostos):
    """
    Valores de los filtros por equipo, vigente desde un periodo dado.
    """
    precio_filtro_aire = models.DecimalField('CU Filtro Aire', max_digits=18, decimal_places=3)
    precio_filtro_combustible = models.DecimalField('CU Filtro Combustible', max_digits=18, decimal_places=3)
    precio_filtro_hidraulico = models.DecimalField('CU Filtro Hidráulico', max_digits=18, decimal_places=3)
    precio_filtro_lubricante = models.DecimalField('CU Filtro Lubricante', max_digits=18, decimal_places=3)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'valor de lubricante'
        verbose_name_plural = 'valores de lubricantes'


class TrenRodajeParametros(BaseParametrosCostos):
    # neumáticos
    vida_util_neumatico = models.IntegerField('vida util estimada (h)', null=True)
    cantidad_neumaticos = models.IntegerField('neumáticos por equipo', null=True)
    medidas = models.CharField('medidas', max_length=24, null=True)

    # orugas
    factor_basico = models.DecimalField('factor básico', max_digits=5, decimal_places=2, null=True)
    impacto = models.DecimalField('impacto', max_digits=5, decimal_places=2, null=True)
    abracion = models.DecimalField('abración', max_digits=5, decimal_places=2, null=True)
    z = models.DecimalField('z', max_digits=5, decimal_places=2, null=True)

    class Meta:
        verbose_name = 'parámetro de tren de rodaje'
        verbose_name_plural = 'parámetros de tren de rodaje'


    @property
    def orugas_costo_USD_hora(self):
        try:
            return self.z * (self.factor_basico + self.impacto + self.abracion)
        except TypeError:
            return 0

    @property
    def neumaticos_cambios_por_anio(self):
        param = self.parametros_gral
        if param:
            return round(self.vida_util_neumatico / param.horas_trabajo_anio, 2)
        return 0


class TrenRodajeValores(BaseParametrosCostos):
    # Neumáticos
    precio_neumatico = models.DecimalField('CU Neumático', max_digits=18, decimal_places=3)

    # Orugas
    # NO HAY VALORES CAMBIANTES MAS QUE EL DOLAR

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'valor de tren de rodaje'
        verbose_name_plural = 'valores de tren de rodaje'

    @property
    def costo_neumaticos_pesos_hora(self):
        param = self.parametros_gral
        parametros = TrenRodajeParametros.objects.filter(
            valido_desde__fecha_inicio__lte=self.valido_desde.fecha_inicio
            ).order_by('-valido_desde__fecha_inicio').first()
        if param and parametros:
            costo = (
                self.precio_neumatico * parametros.cantidad_neumaticos *
                parametros.neumaticos_cambios_por_anio) / param.horas_trabajo_anio
            return costo
        return 0

    @property
    def costo_neumaticos_pesos_mes(self):
        if self.parametros_gral:
            return self.parametros_gral.horas_trabajo_anio * self.costo_neumaticos_pesos_hora / 12
        return 0

    @property
    def costo_orugas_pesos_hora(self):
        parametros = TrenRodajeParametros.objects.filter(
            valido_desde__fecha_inicio__lte=self.valido_desde.fecha_inicio
            ).order_by('-valido_desde__fecha_inicio').first()
        if self.parametros_gral and parametros:
            return self.parametros_gral.valor_dolar * parametros.orugas_costo_USD_hora
        return 0

    @property
    def costo_orugas_pesos_mes(self):
        if self.parametros_gral:
            return self.parametros_gral.horas_trabajo_anio * self.costo_orugas_pesos_hora / 12
        return 0

    @property
    def costo_total_pesos_hora(self):
        return self.costo_neumaticos_pesos_hora + self.costo_orugas_pesos_hora

    @property
    def costo_total_pesos_mes(self):
        return self.costo_neumaticos_pesos_mes + self.costo_orugas_pesos_mes


class PosesionParametros(BaseParametrosCostos):
    posesion_hs = models.IntegerField('periodo de posesion (h)')
    precio_del_activo = models.IntegerField('precio del activo (USD)')
    residual = models.DecimalField('residual', max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = 'parámetro de posesión'
        verbose_name_plural = 'parámetros de posesion'

    @property
    def posesion_en_anios(self):
        if self.parametros_gral:
            return round(self.posesion_hs / self.parametros_gral.horas_trabajo_anio, 2)
        return 0

    @property
    def residual_en_USD(self):
        return self.residual * self.precio_del_activo


class PosesionValores(BaseParametrosCostos):
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

    class Meta:
        verbose_name = 'valor de posesión'
        verbose_name_plural = 'valores de posesión'

    @property
    def costo_anual(self):
        valor_dolar = self.parametros_gral.valor_dolar if self.parametros_gral else 0
        parametros = PosesionParametros.objects.filter(
            valido_desde__fecha_inicio__lte=self.valido_desde.fecha_inicio
            ).order_by('-valido_desde__fecha_inicio').first()
        if parametros:
            #=+(L6-N6)*$F$170/K6+(O6++P6+Q6+R6+S6+T6+U6+V6)*12
            costo = (
                (parametros.precio_del_activo - parametros.residual_en_USD) * valor_dolar / parametros.posesion_en_anios
            ) + (self.seguros + self.ruta + self.vtv + self.certificacion +
                 self.habilitaciones + self.rsv + self.vhf + self.impuestos) * 12
            return costo
        return 0

    @property
    def costo_total_pesos_mes(self):
        return self.costo_anual / 12

    @property
    def costo_total_pesos_hora(self):
        if self.parametros_gral:
            return self.costo_anual / self.parametros_gral.horas_trabajo_anio
        return 0


class ReparacionesParametros(BaseParametrosCostos):
    factor_basico = models.DecimalField('factor básico de reparación', max_digits=18, decimal_places=2)
    multiplicador = models.DecimalField('multiplicador de duración prolongada', max_digits=18, decimal_places=2)

    class Meta:
        verbose_name = 'parámetro de reparación'
        verbose_name_plural = 'parámetros de reparaciones'


class ReparacionesValores(BaseParametrosCostos):

    # NO HAY VALORES CAMBIANTES
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'valor de reparación'
        verbose_name_plural = 'valores de reparaciones'

    @property
    def costo_total_pesos_hora(self):
        parametros = ReparacionesParametros.objects.filter(
            valido_desde__fecha_inicio__lte=self.valido_desde.fecha_inicio
            ).order_by('-valido_desde__fecha_inicio').first()
        if self.parametros_gral and parametros:
            return parametros.factor_basico * parametros.multiplicador * self.parametros_gral.valor_dolar
        return 0

    @property
    def costo_total_pesos_mes(self):
        if self.parametros_gral:
            self.costo_total_pesos_hora * self.parametros_gral.horas_trabajo_anio / 12
        return 0


class ManoObraValores(BaseParametrosCostos):
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

    class Meta:
        verbose_name = 'valor de equipo alquilado'
        verbose_name_plural = 'valores de equipos alquilados'


class CostoEquipoValores(BaseParametrosCostos):
    markup = models.DecimalField('Mark Up (%)', decimal_places=2, max_digits=18)

    history = HistoricalRecords()
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

    ¡¡No hay ejemlpos!!

    COSTO_ALQUILER_ZILLE = EquipoAlquiladoValores

    """

    class Meta:
        verbose_name = 'valor de costo equipo'
        verbose_name_plural = 'valores de costo de equipo'


class AsistenciaEquipo(BaseModel):
    """
    Representa la asistencia de equipos un día dado.
    """
    dia = models.DateField(verbose_name='día')
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'dia de asistencia de equipo a cc'
        verbose_name_plural = 'dias de asistencias de equipo a cc'

    def __str__(self):
        return self.dia


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

    def __str__(self):
        return "{} en {}".format(self.equipo, self.centro_costo)
