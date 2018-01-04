from django.core.exceptions import ValidationError
from django.db import models

from model_utils.managers import QueryManager

from core.models import EstServicio, Operarios, Obras, Equipos
from documento.models import Ri
from parametros.models import Funcion, Situacion, FamiliaEquipo, TipoCosto, Periodo
from zweb_utils.models import BaseModel


class Alarma(models.Model):
    """
    Ok
    """
    alarmaid = models.AutoField(db_column='ALARMAID', primary_key=True)
    fecha = models.DateField(db_column='FECHA', blank=True, null=True)
    comentario = models.TextField(db_column='COMENTARIO', blank=True, null=True)
    fecha_previa = models.DateField(db_column='FECHA_PREVIA', blank=True, null=True)
    ri_id = models.ForeignKey(Ri, db_column='RI_ID', blank=True, null=True)
    nombre = models.CharField(db_column='NOMBRE', max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'alarma'
        verbose_name = "alarma"
        verbose_name_plural = "alarmas"

    def __str__(self):
        return "{} ({})".format(self.nombre, self.fecha)


class Combustible(models.Model):
    """
    OK
    """
    id = models.AutoField(db_column='COMBUSTIBLEID', primary_key=True)
    estacion = models.ForeignKey(EstServicio, db_column='ESTACIONID', related_name="consumo")
    fecha = models.DateField(db_column='FECHA')
    cantidad = models.FloatField(db_column='CANTIDAD')
    responsable = models.CharField(db_column='RESPONSABLE', max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'combustible'
        verbose_name = "entrega de combustible"
        verbose_name_plural = "entregas de combustible"

    def __str__(self):
        return "{} lt ({})".format(self.cantidad, self.estacion.nombre)


class Registro(models.Model):

    DIA_CHOICE = (
        ('otro', 'OTRO'),
        ('SAB', 'SÁBADO'),
        ('DOM', 'DOMINGO'),
    )
    id = models.AutoField(db_column='ID', primary_key=True)
    # horario en Parte diario
    partediario = models.OneToOneField(
            'registro.Partediario', verbose_name="Parte Diario", blank=True, null=True,
            related_name="registro_horario")
    especial = models.BooleanField(db_column='ESPECIAL', verbose_name='¿Se considera día especial?')
    dia = models.CharField(db_column='DIA', max_length=16, choices=DIA_CHOICE, verbose_name="Tipo de día",
                           help_text="Indica si es sábado, domingo o otro.")
    fecha = models.CharField(db_column='FECHA', max_length=16)
    hs_salida = models.TimeField(db_column='HS_SALIDA', blank=True, null=True)
    hs_llegada = models.TimeField(db_column='HS_LLEGADA', blank=True, null=True)
    hs_inicio = models.TimeField(db_column='HS_INICIO', blank=True, null=True)
    hs_fin = models.TimeField(db_column='HS_FIN', blank=True, null=True)
    hs_ialmuerzo = models.TimeField(db_column='HS_IALMUERZO', blank=True, null=True)
    hs_falmuerzo = models.TimeField(db_column='HS_FALMUERZO', blank=True, null=True)
    hs_normal = models.TimeField(db_column='HS_NORMAL', blank=True, null=True)
    hs_viaje = models.TimeField(db_column='HS_VIAJE', blank=True, null=True)
    hs_almuerzo = models.TimeField(db_column='HS_ALMUERZO', blank=True, null=True)
    hs_50 = models.TimeField(db_column='HS_50', blank=True, null=True)
    hs_100 = models.TimeField(db_column='HS_100', blank=True, null=True)
    hs_total = models.TimeField(db_column='HS_TOTAL', blank=True, null=True)
    hs_tarea = models.TimeField(db_column='HS_TAREA', blank=True, null=True)

    class Meta:
        db_table = 'registro'
        verbose_name = "registro horario"
        verbose_name_plural = "registros horario"

    def __str__(self):
        return "Registro de horario {}".format(self.id)


class RegistroEquipo(models.Model):
    MATERIALES = (
        ('agua', "Agua"),
        ('arcilla', "Arcilla"),
        ('arena', "Arena"),
        ('calcareo', "Calcareo"),
        ('destape', "Destape"),
        ('otro', "Otro"),
        ('relleno', "Relleno"),
        ('yeso', "Yeso"),
    )

    id = models.AutoField(db_column='ID', primary_key=True)
    equipo = models.ForeignKey(Equipos, db_column='EQUIPO')
    # equipo en Parte diario
    partediario = models.OneToOneField(
            'registro.Partediario', verbose_name="Parte Diario", blank=True, null=True, related_name="registro_equipo")
    ini_horo = models.CharField(verbose_name="Inicio Horómetro", db_column='INI_HORO', max_length=32, blank=True, null=True)
    fin_horo = models.CharField(verbose_name="Fin Horómetro", db_column='FIN_HORO', max_length=32, blank=True, null=True)
    ini_odo = models.CharField(verbose_name="Inicio Odómetro", db_column='INI_ODO', max_length=32, blank=True, null=True)
    fin_odo = models.CharField(verbose_name="Fin Odómetro", db_column='FIN_ODO', max_length=32, blank=True, null=True)
    cant_combustible = models.CharField(verbose_name="Litros combustible", db_column='CANT_COMBUSTIBLE', max_length=32, blank=True, null=True)
    est_servicio = models.CharField(verbose_name="Nombre plataforma", db_column='EST_SERVICIO', max_length=64, blank=True, null=True)
    tarea = models.TextField(db_column='TAREA', blank=True, null=True)
    datos_carga = models.IntegerField(verbose_name="¿Hay datos de cargas?", db_column='DATOS_CARGA')
    estacion_servicio = models.ForeignKey(EstServicio, verbose_name="Plataforma de combustible", db_column='IDSERVICIO', blank=True, null=True)

    # añado materiales a este modelo
    # material = models.CharField(verbose_name="Material Transportado", choices=MATERIALES, max_length=255, blank=True, null=True)
    # cantidad = models.FloatField(verbose_name="Cantidad", blank=True, null=True)
    # distancia = models.FloatField(verbose_name="Distancia", blank=True, null=True)
    # viajes = models.PositiveSmallIntegerField(verbose_name="Cantidad de viajes", blank=True, null=True)
    # cantera_cargadero = models.CharField(verbose_name="Cantera/Cargadero", max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'registro_equipo'
        verbose_name = "registro vehícular"
        verbose_name_plural = "registros vehículares"

    def __str__(self):
        return "Registro de equipo ID {}".format(self.id)


class Partediario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    situacion = models.ForeignKey(Situacion, db_column='SITUACION', default=1, null=True)

    # numero no debe ser vacio ni repetirse
    numero = models.CharField(db_column='NUMERO', max_length=16, blank=True, null=True)
    operario = models.ForeignKey(Operarios, db_column='OPERARIO')
    funcion = models.ForeignKey(Funcion, db_column='FUNCION', null=True)
    fecha = models.DateField(db_column='FECHA')
    obra = models.ForeignKey(Obras, db_column='OBRA', blank=True, null=True)
    observaciones = models.TextField(db_column='OBSERVACIONES', blank=True, null=True)
    # debería ser boolean
    multifuncion = models.BooleanField(db_column='MULTIFUNCION', default=False)
    # debería ser boolean
    desarraigo = models.BooleanField(db_column='DESARRAIGO', default=False)
    comida = models.IntegerField(db_column='COMIDA', blank=True, null=True)
    vianda = models.IntegerField(db_column='VIANDA', blank=True, null=True)
    vianda_desa = models.IntegerField(db_column='VIANDA_DESA', blank=True, null=True)

    class Meta:
        db_table = 'partediario'
        verbose_name = "parte diario"
        verbose_name_plural = "partes diarios"

    def __str__(self):
        return "Parte {}".format(self.numero)

    @staticmethod
    def autocomplete_search_fields():
        return 'operario', 'equipo'


class PrecioHistorico(models.Model):
    fechaalta = models.DateField(db_column='fechaAlta', blank=True, null=True)
    fechabaja = models.DateField(db_column='fechaBaja', blank=True, null=True)
    valor = models.FloatField()
    familia = models.ForeignKey(FamiliaEquipo, blank=True, null=True)
    tipo = models.ForeignKey(TipoCosto, blank=True, null=True)

    class Meta:
        db_table = 'precio_historico'
        verbose_name = 'precio histórico'
        verbose_name_plural = 'precios históricos'


####################################
## CERTIFICACIONES Y PROYECCIONES ##
####################################


class Certificacion(models.Model):
    periodo = models.ForeignKey(Periodo, verbose_name="Periodo", related_name="certificaciones_periodo")
    obra = models.ForeignKey(Obras, limit_choices_to={'es_cc': True}, related_name="certificaciones_obras")

    es_proyeccion = models.BooleanField(verbose_name="Es una proyección", default=False)

    class Meta:
        unique_together = ('periodo', 'obra', 'es_proyeccion')
        verbose_name = 'certificación'
        verbose_name_plural = 'certificaciones'
        permissions = (
            ("can_manage_certificacion", "Puede gestionar certificaciones"),
        )

    def __str__(self):
        return "Certificación de {} en {}".format(self.obra, self.periodo)

    @property
    def render(self):
        if self.es_proyeccion:
            return "Proyección de certificación de {} ({})".format(self.obra, self.periodo)
        return "Certificación de {} ({})".format(self.obra, self.periodo)

    @property
    def total(self):
        return sum(self.items.values_list('monto', flat=True))

    @property
    def total_sin_adicional(self):
        return sum(self.items.filter(concepto='basica').values_list('monto', flat=True))

    @property
    def total_adicional(self):
        return sum(self.items.exclude(concepto='basica').values_list('monto', flat=True))

    @property
    def basicos(self):
        return sum(self.items.filter(concepto='basica').values_list('monto', flat=True))

    @property
    def cambios(self):
        return sum(self.items.filter(concepto='cambios').values_list('monto', flat=True))

    @property
    def reajustes(self):
        return sum(self.items.filter(concepto='reajuste').values_list('monto', flat=True))

    @property
    def reclamos(self):
        return sum(self.items.filter(concepto='reclamos').values_list('monto', flat=True))


class CertificacionItem(BaseModel):

    CONCEPTO = (
        ('basica', 'Básica'),
        ('cambios', 'Órdenes de cambio'),
        ('reajuste', 'Reajuste de precios'),
        ('reclamos', 'Reclamos reconocidos')
    )
    certificacion = models.ForeignKey(Certificacion, verbose_name='certificación', related_name='items')
    concepto = models.CharField('concepto', max_length=16, choices=CONCEPTO, default='basica')
    monto = models.DecimalField(verbose_name="Monto ($)", max_digits=18, decimal_places=2)
    observaciones = models.CharField('observaciones', max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'ítem certificación'
        verbose_name_plural = 'ítemes de certificaciones'

    def __str__(self):
        return "{} ($ {})".format(self.get_concepto_display(), self.monto)


class Materiales(models.Model):

    MATERIALES = (
        ('agua', "Agua"),
        ('arcilla', "Arcilla"),
        ('arena', "Arena"),
        ('calcareo', "Calcareo"),
        ('destape', "Destape"),
        ('otro', "Otro"),
        ('relleno', "Relleno"),
        ('yeso', "Yeso"),
    )
    id = models.AutoField(db_column='ID', primary_key=True)
    material = models.CharField(db_column='MATERIAL', choices=MATERIALES, max_length=255, blank=True, null=True)
    cantidad = models.CharField(db_column='CANTIDAD', max_length=64, blank=True, null=True)
    distancia = models.CharField(db_column='DISTANCIA', max_length=64, blank=True, null=True)
    viajes = models.PositiveSmallIntegerField(db_column='VIAJES', blank=True, null=True)
    cantera_cargadero = models.CharField(db_column='CANTERA_CARGADERO', max_length=255, blank=True, null=True)
    partediario = models.ForeignKey(Partediario, verbose_name="Parte Diario", related_name="materiales_transportados", null=True)

    class Meta:
        db_table = 'materiales'
        verbose_name = "material transportado"
        verbose_name_plural = "materiales transportados"

    def __str__(self):
        return "({}) {} - {}".format(
            self.cantidad, self.material,
            self.cantera_cargadero if self.cantera_cargadero else "Cantera/Cargadero no especificado")


class AjusteCombustible(models.Model):
    periodo = models.ForeignKey(Periodo, related_name="ajustes_combustibles")
    obra = models.ForeignKey(Obras, related_name="ajustes_combustibles_x_obra")
    valor = models.FloatField(verbose_name="valor de ajuste", null=True, blank=True,
                              help_text='Utilice este valor para ajustar el valor arrojado por el informe')
    costo_total = models.FloatField(verbose_name='costo total', null=True, blank=True,
                                    help_text='Si ingresa este valor, se ignorará los registros para el periodo '
                                              'y centro de costo asociados')
    comentarios = models.TextField(verbose_name="comentarios", null=True, blank=True)

    class Meta:
        verbose_name_plural = "ajustes de combustible"
        verbose_name = "ajuste de combustible"
        unique_together = ('periodo', 'obra', )

    def __str__(self):
        return "{} - {}".format(self.periodo, self.obra)

    def clean(self):
        super(AjusteCombustible, self).clean()
        if not any([self.valor, self.costo_total]):
            raise ValidationError('Ingrese al menos un valor (de ajuste o total). Ambos no pueden ser vacio.')
        if all([self.valor, self.costo_total]):
            raise ValidationError('Ingrese "Valor de ajuste" o "Costo Total" pero no ambos.')


class CertificacionInterna(models.Model):
    """
    Servicios prestados a otras Unidades de Negocio. Son certificaciones internas.
    """
    periodo = models.ForeignKey(Periodo, verbose_name="Periodo", related_name="certificaciones_internas_periodo")
    obra = models.ForeignKey(Obras, limit_choices_to={'es_cc': True}, related_name="certificaciones_internas_obras")
    monto = models.FloatField(verbose_name="Monto ($)")

    class Meta:
        unique_together = ('periodo', 'obra', )
        verbose_name = 'certificación interna'
        verbose_name_plural = 'certificaciones internas'

    def __str__(self):
        return "Certificación interna de {} en {}".format(self.obra, self.periodo)
