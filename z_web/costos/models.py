from django.db import models

from core.models import Obras
from parametros.models import Periodo, FamiliaEquipo


class CalculosMixin:

    def recalcular_valor(self, parametros):
        """
        Esta funcion recibe un objeto parámetro, cual tiene un nuevo valor del dolar,
        y recalcula el item para ese monto.
        :param parametros:
        :return:
        """
        nuevo_pd = parametros.pesos_usd
        viejo_pd = self.periodo.parametros_costos.pesos_usd
        if hasattr(self, 'monto'):
            self.monto = nuevo_pd * self.monto / viejo_pd
        elif hasattr(self, 'monto_mes'):
            self.monto_mes = nuevo_pd * self.monto_mes / viejo_pd
        elif hasattr(self, 'monto_hora'):
            self.monto_hora = nuevo_pd * self.monto_hora / viejo_pd


class CostoManoObra(models.Model, CalculosMixin):
    """
    Costos de mano de obra por CC y periodo
    """
    obra = models.ForeignKey(Obras, verbose_name="Centro de Costo", related_name="costos_mo", limit_choices_to={'es_cc':True})
    periodo = models.ForeignKey(Periodo, verbose_name="Periodo", related_name="costos_mo")
    monto = models.FloatField(verbose_name="Monto ($)")

    class Meta:
        unique_together = ('periodo', 'obra', )
        verbose_name_plural = "costos de mano de obra"
        verbose_name = "costo de mano de obra"

    def __str__(self):
        return "{} - {}".format(self.obra, self.periodo)


class CostoSubContrato(models.Model, CalculosMixin):
    """
    Costos por subcontratos
    """
    descripcion = models.CharField(verbose_name="Descripción", max_length=255, blank=True,
                                   help_text="Observaciones opcionales")
    obra = models.ForeignKey(Obras, verbose_name="Centro de costo", related_name="costos_subcontrato",
                             limit_choices_to={'es_cc':True})
    periodo = models.ForeignKey(Periodo, verbose_name="Periodo", related_name="costos_subcontratos")
    monto = models.FloatField(verbose_name="Monto ($)")

    class Meta:
        unique_together = ('periodo', 'obra', )
        verbose_name_plural = "costos por subcontrato"
        verbose_name = "costo de subcontrato"

    def __str__(self):
        return "{0} - {1}{2}".format(
            self.obra, self.periodo,
            "({})".format(self.descripcion) if self.descripcion else '')


class AbstractCosto(models.Model, CalculosMixin):
    """
    Clase genérica para costos comunes
    """
    familia_equipo = models.ForeignKey(FamiliaEquipo, verbose_name="Familia de equipo")
    periodo = models.ForeignKey(Periodo, verbose_name="Periodo")
    monto_hora = models.FloatField(verbose_name="$/hs")
    monto_mes = models.FloatField(verbose_name="$/mes")

    class Meta:
        abstract = True

    def __str__(self):
        return "{} de {} en {}".format(self._meta.verbose_name, self.familia_equipo, self.periodo)

    def set_monto_mes(self, parametros):
        if self.monto_hora:
            self.monto_mes = parametros.dias_mes * parametros.horas_dia * self.monto_hora

    def set_monto_hora(self, parametros):
        if self.monto_mes:
            self.monto_hora = self.monto_mes / parametros.dias_mes / parametros.horas_dia


class LubricanteFluidosHidro(AbstractCosto):

    class Meta:
        unique_together = ('periodo', 'familia_equipo', )
        verbose_name = "costo de lubricantes y fluidos hidráulicos"
        verbose_name_plural = "costos de lubricantes y fluidos hidráulicos"


class TrenRodaje(AbstractCosto):

    class Meta:
        unique_together = ('periodo', 'familia_equipo', )
        verbose_name = "costo de tren de rodaje"
        verbose_name_plural = "costos de tren de rodaje"


class ReserveReparaciones(AbstractCosto):

    class Meta:
        unique_together = ('periodo', 'familia_equipo', )
        verbose_name = "costo de reserva de reparaciones"
        verbose_name_plural = "costos de reserva de reparaciones"


class CostoPosesion(AbstractCosto):
    monto_año = models.FloatField(verbose_name="$/año")

    class Meta:
        unique_together = ('periodo', 'familia_equipo', )
        verbose_name = "costo de posesión"
        verbose_name_plural = "costos de posesión"


class MaterialesTotal(models.Model, CalculosMixin):
    """
    Total de costo de materiales por periodo
    """
    periodo = models.ForeignKey(Periodo, verbose_name="Periodo", related_name="costos_total_materiales")
    obra = models.ForeignKey(Obras, verbose_name="Centro de costo", related_name="costos_total_materiales",
                             limit_choices_to={'es_cc':True})
    monto = models.FloatField(verbose_name="Costo ($)")

    class Meta:
        unique_together = ('periodo', 'obra', )
        verbose_name = "costo total de materiales"
        verbose_name_plural = "costos totales de materiales"

    def __str__(self):
        return "{} - {}".format(self.obra, self.periodo)

# Por ahora, sólo utilizamos los costos por periodo. Utilizar esto cuando sea por día
# class CostoParametroManager(models.Manager):
#     def get_vigente_now(self):
#         return super(CostoParametroManager, self).get_queryset().filter(fecha_baja__isnull=True).latest('fecha_alta')
#
#     def get_vigente_el_dia(self, date):
#         return super(CostoParametroManager, self).get_queryset().filter(
#             Q(fecha_baja__gt=date) | Q(fecha_baja__isnull=True),
#             fecha_alta__lte=date).latest('pk')
#
#     def get_vigente_el_periodo(self, periodo):
#         return super(CostoParametroManager, self).get_queryset().filter(
#             Q(fecha_baja__gte=periodo.fecha_fin) | Q(fecha_baja__isnull=True),
#             fecha_alta__lte=periodo.fecha_inicio)



class CostoParametro(models.Model):
    """
    Parámetros relacionados con los costos por periodo. Se mantiene trazabilidad
    al mantener las fechas de vigencia.
    """
    # objects = models.Manager()
    # vigentes = CostoParametroManager()
    periodo = models.OneToOneField(Periodo, verbose_name="Periodo", related_name="parametros_costos")
    horas_dia = models.PositiveSmallIntegerField(verbose_name="Hs/día", default=6)
    dias_mes = models.PositiveSmallIntegerField(verbose_name="Días/mes", default=20)
    horas_año = models.PositiveIntegerField(verbose_name="Hs/año", default=1440)
    pesos_usd = models.FloatField(verbose_name="$/USD", help_text="Valor del peso argentino frente al dolar.")
    precio_go = models.FloatField(verbose_name="Precio Gasoil", help_text="$/l a granel sin impuestos deducibles")
    # fecha_alta = models.DateField(verbose_name="Fecha de inicio de vigencia", auto_now_add=True,
    #                               help_text="La fecha de inicio de vigencia se establecerá automaticamente al guardar.")
    # fecha_baja = models.DateField(verbose_name="Fecha de fin de vigencia", null=True, default=None,
    #                               help_text="La fecha de fin de vigencia, se establecerá automaticamente al añadir y/o "
    #                                         "modificar los valores de los parámetros de costos")

    def __str__(self):
        return "Parámetros de costos de {}".format(self.periodo)

    class Meta:
        verbose_name = "parametro de costo"
        verbose_name_plural = "parametros de costos"
        permissions = (
            ("can_view_panel_control", "Puede ver Panel de Control"),
            ("can_add_costos_masivo", "Puede ingresar costos masivos"),
            ("can_export_panel_control", "Puede exportar el panel de control")
        )


class ServicioPrestadoUN(models.Model, CalculosMixin):
    """
    Este modelo pasa a registros, ya que no es un costo.
    """
    periodo = models.ForeignKey(Periodo, verbose_name="Periodo", related_name="costos_servicios_xperiodo")
    obra = models.ForeignKey(Obras, verbose_name="Centro de costo", related_name="costos_servicios_xobra",
                             limit_choices_to={'es_cc':True})
    monto = models.FloatField(verbose_name="Costo ($)")

    class Meta:
        unique_together = ('periodo', 'obra', )
        verbose_name = "costo de servicio prestado a UN"
        verbose_name_plural = "costos de servicios prestados a UN"

    def __str__(self):
        return "{} - {}".format(self.obra, self.periodo)


class ArchivosAdjuntosPeriodo(models.Model):
    """
    Adjuntar archivos a un periodo para asociarlos al panel de control
    """
    periodo = models.ForeignKey(Periodo, verbose_name="Periodo", related_name="archivos")
    archivo = models.FileField(verbose_name="archivo", upload_to="adjuntos")
    comentario = models.TextField(verbose_name="comentario", null=True, blank=True)

    class Meta:
        verbose_name = "archivo adjunto de periodo"
        verbose_name_plural = "archivos adjunto de periodos"

    def __str__(self):
        return "{} ({})".format(self.archivo, self.periodo)