from decimal import Decimal as D
from django.core.exceptions import ValidationError
from django.db import models

from model_utils.managers import QueryManager

from core.models import Obras
from parametros.models import Periodo, FamiliaEquipo, Parametro
from zweb_utils.models import BaseModel


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
            ("can_export_panel_control", "Puede exportar el panel de control"),
            ("can_manage_costos", "Puede gestionar costos"),
            ("can_generate_reports", "Puede generar reportes"),
        )


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


#######################################
#  Nuevo sistema de costos
#######################################


class CostoTipo(BaseModel):
    """
    Clasificador de costos. El tipo de costo determina que
    valores podrán cargarse y como éste se calcula.
    """
    RELACIONADO_CON = (
        ('cc', 'Centro de costos'),
        ('eq', 'Equipos')
    )

    UNIDAD_MONTO = (
        ('total', '$'),
        ('x_hs', '$/hs - $/mes - $/año')
    )
    nombre = models.CharField(verbose_name='nombre', max_length=255)
    codigo = models.CharField(
        verbose_name='codigo', max_length=8, unique=True,
        help_text=("Código único para identificar unívocamente el tipo de costo. "
                   "Máximo largo: 8. Se removerán automáticamente espacios y se convertirá a mayúsculas."))
    relacionado_con = models.CharField(
        'relacionado con', max_length=2, choices=RELACIONADO_CON, default='cc',
        help_text='Especifique si el costo estará asociado a un centro de costos, o asociado a un equipo.')
    unidad_monto = models.CharField(
        'monto expresado en', max_length=8, choices=UNIDAD_MONTO, default='total',
        help_text='Especifique si el valor del monto estará expresado en $ (total) o segmentado en $/hs, $/mes o $/año.')

    class Meta:
        verbose_name = 'tipo de costos'
        verbose_name_plural = 'tipos de costos'

    def __str__(self):
        return self.nombre

    @property
    def es_monto_segmentado(self):
        return self.unidad_monto == 'x_hs'

    @property
    def es_por_cc(self):
        return self.relacionado_con == 'cc'

    def clean(self):
        super(CostoTipo, self).clean()
        self.codigo = self.codigo.strip().replace(" ", "").upper()
        if self.relacionado_con == 'cc' and self.unidad_monto != 'total':
            raise ValidationError({'unidad_monto': "Si selecciona Centro de costos, debe seleccionar '$' como unidad de monto."})
        if self.relacionado_con == 'eq' and self.unidad_monto != 'x_hs':
            raise ValidationError({'unidad_monto': "Si selecciona Equipos, debe seleccionar '$/hs' como unidad de monto."})


class Costo(BaseModel):
    """
    Representa un costo de un proyecto y/o equipo. Dependiendo de su tipo, este
    tendrá distintos campos requeridos y distintos será el modo de calcular junto a otros costos.
    """
    tipo_costo = models.ForeignKey(CostoTipo, verbose_name='tipo de costo')
    periodo = models.ForeignKey(Periodo, verbose_name="periodo")
    observacion = models.CharField(verbose_name='observación', max_length=255, null=True, blank=True)

    centro_costo = models.ForeignKey(
        Obras, verbose_name="centro de costo", related_name="mis_costos",
        limit_choices_to={'es_cc':True}, null=True)

    familia_equipo = models.ForeignKey(
        FamiliaEquipo, verbose_name="Familia de equipo", null=True,
        related_name='costos_de_la_familia')

    monto_total = models.DecimalField(verbose_name="$", decimal_places=2, max_digits=18, null=True, blank=True)
    monto_hora = models.DecimalField(verbose_name="$/hs", decimal_places=2, max_digits=18, null=True, blank=True)
    monto_mes = models.DecimalField(verbose_name="$/mes", decimal_places=2, max_digits=18, null=True, blank=True)
    monto_anio = models.DecimalField(verbose_name="$/año", decimal_places=2, max_digits=18, null=True, blank=True)

    class Meta:
        verbose_name = 'costo'
        verbose_name_plural = 'costos'
        ordering = ('periodo', )

    def clean(self):
        super(Costo, self).clean()
        is_unique_qs = Costo.objects.filter(periodo=self.periodo, tipo_costo=self.tipo_costo)
        non_unique = None

        if self.tipo_costo.es_por_cc:
            if not self.centro_costo:
                raise ValidationError("El centro de costo es obligatorio para el tipo de costo '{}'".format(self.tipo_costo))
            if not self.monto_total:
                raise ValidationError("El monto total es obligatorio")

            is_unique_qs = is_unique_qs.filter(centro_costo=self.centro_costo)
            non_unique = 'centro de costo'

        else:
            if not self.familia_equipo:
                raise ValidationError("La familia de equipo es obligatorio para el tipo de costo '{}'".format(self.tipo_costo))

            if not any([self.monto_hora, self.monto_mes, self.monto_anio]):
                raise ValidationError("Debe ingresar al menos un monto para calcular los restantes.")

            is_unique_qs = is_unique_qs.filter(familia_equipo=self.familia_equipo)
            non_unique = 'familia de equipo'
        if self.pk:
            is_unique_qs = is_unique_qs.exclude(pk=self.pk)
        if is_unique_qs.exists():
            raise ValidationError("El costo para el periodo {} y {} ya existe.".format(self.periodo, non_unique))

    def __str__(self):
        return "Costo de {} - {} - {}".format(
            self.tipo_costo,
            self.periodo,
            self.centro_costo if self.tipo_costo.es_por_cc else self.familia_equipo)

    def recalcular_valor(self, parametros):
        """
        Esta funcion recibe un objeto parámetro, cual tiene un nuevo valor del dolar,
        y recalcula el item para ese monto.
        """
        nuevo_pd = D("{}".format(parametros.pesos_usd))
        viejo_pd = D("{}".format(self.periodo.parametros_costos.pesos_usd))
        if self.tipo_costo.es_monto_segmentado:
            if self.monto_hora:
                self.monto_hora = nuevo_pd * self.monto_hora / viejo_pd
            if self.monto_mes:
                self.monto_mes = nuevo_pd * self.monto_mes / viejo_pd
            if self.monto_anio:
                self.monto_anio = nuevo_pd * self.monto_anio / viejo_pd
        else:
            self.monto_total = nuevo_pd * self.monto_total / viejo_pd

    def calcular_otros_monto(self, parametros):
        """
        Calcula los distintos montos segmentados, basado en el dato dado.
        """
        if self.tipo_costo.es_monto_segmentado:
            new_values = {}
            if self.monto_hora:
                new_values["monto_mes"] = parametros.dias_mes * parametros.horas_dia * self.monto_hora
                new_values["monto_anio"] = parametros.horas_año * self.monto_hora
            elif self.monto_mes:
                new_values["monto_hora"] = self.monto_mes / parametros.dias_mes / parametros.horas_dia
                new_values["monto_anio"] = parametros.horas_año * new_values["monto_hora"]
            elif self.monto_anio:
                new_values["monto_hora"] = self.monto_anio / parametros.horas_año
                new_values["monto_mes"] = new_values["monto_hora"] * parametros.horas_dia * parametros.dias_mes
            # actualizar sólo si no existe el valor
            for k, v in new_values.items():
                if not getattr(self, k):
                    setattr(self, k, v)

    def save(self, *args, **kwargs):
        """
        Calculo costos restantes basados en los parámetros y los valores existentes
        """
        if self.periodo.parametros_costos:
            self.calcular_otros_monto(self.periodo.parametros_costos)
        super(Costo, self).save(*args, **kwargs)

    # def get_fields(self):
    #     """
    #     Deuelve el listado correcto de field según el tipo de costo
    #     """
    #     fields = ['tipo_costo', 'periodo', 'observacion']
    #     if self.tipo_costo.es_por_cc:
    #         fields.append('centro_costo')
    #     else:
    #         fields.append('familia_equipo')
    #     if self.tipo_costo.es_monto_segmentado:
    #         fields.extend(['monto_hora', 'monto_mes', 'monto_anio'])
    #     else:
    #         fields.append('monto_total')
    #     return fields

    @property
    def render(self):
        if self.tipo_costo.es_por_cc:
            return "{} | CC: {}".format(self, self.centro_costo)
        else:
            return "{} | Equipo: {}".format(self, self.familia_equipo)


class AvanceObra(BaseModel):
    """
    Esta entidad registra el avance de obra real para una obra y periodo específico.
    """
    periodo = models.ForeignKey(Periodo, verbose_name="periodo")
    centro_costo = models.ForeignKey(
        Obras, verbose_name="centro de costo", related_name="mis_avances",
        limit_choices_to={'es_cc':True})
    avance = models.DecimalField(verbose_name='avance', decimal_places=3, max_digits=18)
    observacion = models.CharField(verbose_name='observación', max_length=255, null=True, blank=True)

    es_proyeccion = models.BooleanField(verbose_name="Es una proyección", default=False)

    class Meta:
        verbose_name = 'avance de obra'
        verbose_name_plural = 'avances de obra'
        ordering = ('periodo', )
        unique_together = ('periodo', 'centro_costo', 'es_proyeccion')

    def __str__(self):
        return "Avance de {} en {} - {:.1f} %".format(self.centro_costo, self.periodo, self.avance)

    @property
    def render(self):
        return "Avance de obra de {} ({})".format(self.centro_costo, self.periodo)
