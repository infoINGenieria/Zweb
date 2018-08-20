from decimal import Decimal as D

from django.db import models

from simple_history.models import HistoricalRecords

from parametros.models import Periodo
from core.models import Equipos, Obras
from zweb_utils.models import BaseModel


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

    # FILTROS
    @property
    def cambio_filtro_aire(self):
        """
        Igual a los cambios de lubricante
        """
        return self.cambios_lubricante_por_anio

    @property
    def cambio_filtro_combustible(self):
        """
        Igual a los cambios de lubricante
        """
        return self.cambios_lubricante_por_anio

    @property
    def cambio_filtro_hidraulico(self):
        """
        Igual a los cambios de hidraulico
        """
        return self.cambios_hidraulico_por_anio

    @property
    def cambio_filtro_lubricante(self):
        """
        Igual a los cambios de lubricante
        """
        return self.cambios_lubricante_por_anio



class LubricantesValores(ValoresMixin, BaseParametrosCostos):
    """
    Valores de los filtros por equipo, vigente desde un periodo dado.
    """
    precio_filtro_aire = models.DecimalField('CU Filtro Aire', max_digits=18, decimal_places=3)
    precio_filtro_combustible = models.DecimalField('CU Filtro Combustible', max_digits=18, decimal_places=3)
    precio_filtro_hidraulico = models.DecimalField('CU Filtro Hidráulico', max_digits=18, decimal_places=3)
    precio_filtro_lubricante = models.DecimalField('CU Filtro Lubricante', max_digits=18, decimal_places=3)

    history = HistoricalRecords()

    model_parametros = LubricantesParametros

    class Meta:
        verbose_name = 'valor de lubricante'
        verbose_name_plural = 'valores de lubricantes'

    @property
    def costo_lubricante_pesos_hora(self):
        param = self.parametros_gral
        if param and self.mis_parametros:
            costo = (self.mis_parametros.consumo_medio * param.precio_lubricante) + (
                self.mis_parametros.cambios_lubricante_por_anio *
                self.mis_parametros.volumen_lubricante_por_cambio *
                param.precio_lubricante / param.horas_trabajo_anio
            )
            return costo
        return 0

    @property
    def costo_hidraulico_pesos_hora(self):
        param = self.parametros_gral
        if param and self.mis_parametros:
            costo = (
                self.mis_parametros.volumen_hidraulico_por_cambio *
                self.mis_parametros.cambios_hidraulico_por_anio *
                param.precio_hidraulico / param.horas_trabajo_anio)
            return costo
        return 0

    @property
    def costo_filtro_aire_pesos_anio(self):
        if not self.mis_parametros:
            return 0
        return self.precio_filtro_aire * self.mis_parametros.cambio_filtro_aire

    @property
    def costo_filtro_combustible_pesos_anio(self):
        if not self.mis_parametros:
            return 0
        return self.precio_filtro_combustible * self.mis_parametros.cambio_filtro_combustible

    @property
    def costo_filtro_hidraulico_pesos_anio(self):
        if not self.mis_parametros:
            return 0
        return self.precio_filtro_hidraulico * self.mis_parametros.cambio_filtro_hidraulico

    @property
    def costo_filtro_lubricante_pesos_anio(self):
        if not self.mis_parametros:
            return 0
        return self.precio_filtro_lubricante * self.mis_parametros.cambio_filtro_lubricante

    @property
    def costo_filtro_pesos_hora(self):
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
            self.costo_lubricante_pesos_hora +
            self.costo_hidraulico_pesos_hora +
            self.costo_filtro_pesos_hora)

    @property
    def costo_total_pesos_mes(self):
        param = self.parametros_gral
        if param:
            return self.costo_total_pesos_hora * param.horas_trabajo_anio / 12
        return 0


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
            return D(self.vida_util_neumatico) / param.horas_trabajo_anio
        return 0


class TrenRodajeValores(ValoresMixin, BaseParametrosCostos):
    # Neumáticos
    precio_neumatico = models.DecimalField('CU Neumático', max_digits=18, decimal_places=3)

    # Orugas
    # NO HAY VALORES CAMBIANTES MAS QUE EL DOLAR

    history = HistoricalRecords()

    model_parametros = TrenRodajeParametros

    class Meta:
        verbose_name = 'valor de tren de rodaje'
        verbose_name_plural = 'valores de tren de rodaje'

    @property
    def costo_neumaticos_pesos_hora(self):
        param = self.parametros_gral
        if param and self.mis_parametros:
            costo = (
                self.precio_neumatico * self.mis_parametros.cantidad_neumaticos *
                self.mis_parametros.neumaticos_cambios_por_anio
                ) / param.horas_trabajo_anio
            return costo
        return 0

    @property
    def costo_neumaticos_pesos_mes(self):
        if self.parametros_gral:
            return self.parametros_gral.horas_trabajo_anio * self.costo_neumaticos_pesos_hora / 12
        return 0

    @property
    def costo_orugas_pesos_hora(self):
        if self.parametros_gral and self.mis_parametros:
            return self.parametros_gral.valor_dolar * self.mis_parametros.orugas_costo_USD_hora
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
            return D(self.posesion_hs) / self.parametros_gral.horas_trabajo_anio
        return 0

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


class ReparacionesValores(ValoresMixin, BaseParametrosCostos):

    # NO HAY VALORES CAMBIANTES
    history = HistoricalRecords()

    model_parametros = ReparacionesParametros

    class Meta:
        verbose_name = 'valor de reparación'
        verbose_name_plural = 'valores de reparaciones'

    @property
    def costo_total_pesos_hora(self):
        if self.parametros_gral and self.mis_parametros:
            return self.mis_parametros.factor_basico * self.mis_parametros.multiplicador * self.parametros_gral.valor_dolar
        return 0

    @property
    def costo_total_pesos_mes(self):
        if self.parametros_gral:
            return self.costo_total_pesos_hora * self.parametros_gral.horas_trabajo_anio / 12
        return 0


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
            return 0
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
            if not hasattr(self, '_errors'):
                self._errors = []
            self._errors.append("No hay %s" % parametros._meta.verbose_name)
            return 0

    @property
    def costo_equipo_propio(self):
        if self.equipo.es_alquilado:
            return 0
        self.costo_equipo_calculado = (
            self.costo_mensual_del_activo + self.costo_mensual_del_activo_con_mo
            ) * self.markup / 100
        self.save()
        return self.costo_equipo_calculado

    @property
    def costo_mensual_del_activo_con_mo(self):
        # costo_mensual_del_activo_con_mo = (costo_mensual_del_activo * ManoObraValores.taller) / total_flota
        mo_valor = self.get_dato_vigente(ManoObraValores)
        total_flota = self.get_dato_vigente(TotalFlota)
        if mo_valor and total_flota:
            taller = mo_valor.taller
            flota = total_flota.monto
            self.costo_mensual_del_activo_con_mo_calculado = (self.costo_mensual_del_activo * taller) / flota
        else:
            self.costo_mensual_del_activo_con_mo_calculado = 0
        self.save()
        return self.costo_mensual_del_activo_con_mo_calculado

    @property
    def costo_equipo_alquilado(self):
        if not self.equipo.es_alquilado:
            return 0
        equipo_alquilado = self.get_dato_vigente(EquipoAlquiladoValores)
        if equipo_alquilado:
            self.costo_equipo_calculado = equipo_alquilado.alquiler
        else:
            self.costo_equipo_calculado = 0
        self.save()
        return self.costo_equipo_calculado

    class Meta:
        verbose_name = 'valor de costo equipo'
        verbose_name_plural = 'valores de costo de equipo'


class TotalFlota(BaseModel):
    valido_desde = models.OneToOneField(Periodo, verbose_name="válido desde")
    monto = models.DecimalField('Total Flota($)', decimal_places=2, max_digits=18)

    def calcular_total_flota(self):
        """
        Recalcular todos los valores válidos para el periodo correspondiente.
        """
        monto_aux = 0
        for equipo in Equipos.objects.filter(fecha_baja__isnull=True):
            valor = CostoEquipoValores.objects.filter(
                equipo=equipo,
                valido_desde__fecha_inicio__lte=self.valido_desde.fecha_inicio
            ).order_by('-valido_desde__fecha_inicio').first()
            monto_aux += valor.costo_mensual_del_activo if valor else 0
        self.monto = monto_aux
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
        unique_together = ('asistencia', 'equipo', 'centro_costo')

    def __str__(self):
        return "{} en {}".format(self.equipo, self.centro_costo)
