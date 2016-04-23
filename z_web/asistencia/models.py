from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from simple_history.models import HistoricalRecords

from organizacion.models import Persona, Proyecto
from zweb_utils.models import BaseModelWithHistory, BaseModel


class EstadoAsistencia(BaseModelWithHistory):
    """
    Representa los posibles valores para la asistencia de cada persona.

    """
    situacion = models.CharField("situación", max_length=255)
    codigo = models.CharField("código", max_length=5, unique=True)
    observaciones = models.CharField("observaciones", max_length=255,
                                     blank=True, null=True)
    no_ocioso = models.BooleanField("No está ocioso", default=False,
                                    help_text="Seleccione esta opción para indicar "
                                              "que el estado no implica ociosidad por parte del empleado")
    activo = models.BooleanField("activo", default=True)
    history = HistoricalRecords()


    class Meta:
        verbose_name = "estado de asistencia"
        verbose_name_plural = "estados de asistencias"
        ordering = ('situacion', )

    def __str__(self):
        return "{} - {}".format(self.codigo, self.situacion)


class ResponsableAsistencia(BaseModelWithHistory):
    """
    Representa al responsable del proyecto, junto a sus configuraciones.

    """
    persona = models.ForeignKey(Persona, verbose_name="persona", related_name="responsable_rel", null=True)
    proyecto = models.OneToOneField(Proyecto, verbose_name="proyecto", related_name="responsable_rel", null=True)
    history = HistoricalRecords()

    def __str__(self):
        return "{} responsable de {}".format(
            self.persona, self.proyecto
        )

    class Meta:
        verbose_name = "responsable"
        verbose_name_plural = "responsables"
        unique_together = ('persona', 'proyecto', )


class Asistencia(BaseModelWithHistory):
    """
    Representa la asistencia para un día y proyecto específico.

    """
    fecha = models.DateField("Fecha de presentismo")
    proyecto = models.ForeignKey(Proyecto, related_name="asistencias")
    responsable = models.ForeignKey(ResponsableAsistencia, related_name="mis_asistencias", null=True)
    nombre_responsable = models.CharField(
        "Nombre del responsable", max_length=255,
        help_text="Se completará automaticamente con el responsable del proyecto seleccionado")
    nombre_proyecto = models.CharField(
        "Nombre del proyecto", max_length=255,
        help_text="Se completará automaticamente con el nombre del proyecto seleccionado.")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "asistencia"
        verbose_name_plural = "asistencias"
        unique_together = ('fecha', 'proyecto', )

    def __str__(self):
        return "{} - {}".format(self.fecha, self.proyecto)

    def save(self, *args, **kwargs):
        self.nombre_proyecto = self.proyecto.nombre
        try:
            if not self.nombre_responsable:
                self.nombre_responsable = "{}".format(self.proyecto.responsable_rel.persona)
        except:
            pass
        super(Asistencia, self).save(*args, **kwargs)

    @property
    def total_items(self):
        return "{} items".format(self.items.count())

    @property
    def filename_report(self):
        return 'Asistencia-{}-{}'.format(self.proyecto, self.fecha.strftime("%d-%m-%Y")).replace(' ', '_')


class RegistroAsistencia(BaseModelWithHistory):
    """
    Representa el dato sobre la asistencia de una persona para una
    Asistencia en particular.

    """
    asistencia = models.ForeignKey(Asistencia, related_name="items")
    persona = models.ForeignKey(Persona, related_name='registro_asistencia')
    estado = models.ForeignKey(EstadoAsistencia, verbose_name="estado de presentismo", default=settings.ESTADO_DEFAULT)
    codigo_estado = models.CharField(
        "Código", max_length=5, help_text="Se establecerá automaticamente con "
                                          "el código del estado seleccionado.")
    observaciones = models.CharField("observaciones", max_length=255,
                                     blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "registro de asistencia"
        verbose_name_plural = "registros de asistencia"
        unique_together = ('asistencia', 'persona', )

    def __str__(self):
        return "{} - {}".format(self.persona, self.asistencia)

    def save(self, *args, **kwargs):
        self.codigo_estado = self.estado.codigo
        try:
            usuario = self.asistencia.proyecto.responsable_rel.persona.usuario
        except AttributeError:
            usuario = None
        if self.estado.codigo in settings.ESTADO_BAJA:
            MovimientoPersona.generar_baja(self.persona, fecha=self.asistencia.fecha, usuario=usuario)
        elif not self.persona.fecha_baja is None:
            MovimientoPersona.generar_alta(self.persona, fecha=self.asistencia.fecha, usuario=usuario)
        super(RegistroAsistencia, self).save(*args, **kwargs)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "registro de asistencia"
        verbose_name_plural = "registros de asistencia"
        unique_together = ('asistencia', 'persona', )


class MovimientoPersona(BaseModel):
    SITUACION_ALTA = 1
    SITUACION_BAJA = 2

    TIPO_SITUACION = (
        (SITUACION_ALTA, "ALTA"),
        (SITUACION_BAJA, "BAJA"),
    )
    persona = models.ForeignKey(Persona)
    situacion = models.SmallIntegerField(verbose_name="situacion", choices=TIPO_SITUACION, default=1)
    fechahora = models.DateTimeField(verbose_name="fecha y hora")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="realizado por", null=True, blank=True)

    class Meta:
        verbose_name = "movimiento de persona"
        verbose_name_plural = "movimiento de personas"

    @classmethod
    def _generar_movimiento(cls, persona, tipo, fecha, usuario=None):
        movimiento = MovimientoPersona(persona=persona, situacion=tipo, fechahora=fecha)
        if usuario:
           movimiento.usuario = usuario
        movimiento.save()
        if tipo == cls.SITUACION_ALTA:
            persona.fecha_baja = None
        else:
            persona.fecha_baja = timezone.now()
        persona.save()

    @classmethod
    def generar_baja(cls, persona, fecha, usuario=None):
        cls._generar_movimiento(persona, cls.SITUACION_BAJA, fecha, usuario)

    @classmethod
    def generar_alta(cls, persona, fecha, usuario=None):
        cls._generar_movimiento(persona, cls.SITUACION_ALTA, fecha, usuario)


def generar_alta_persona(sender, instance, created, **kwargs):
    if created:
        MovimientoPersona.generar_alta(persona=instance, fecha=instance.created_at)


post_save.connect(generar_alta_persona, sender=Persona)
