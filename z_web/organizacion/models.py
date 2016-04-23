from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings

from simple_history.models import HistoricalRecords

from core.models import PerfilTecnico
from organizacion.managers import ProyectoManager, ProyectoConPersonasManager, PersonaManager
from parametros.models import Funcion
from zweb_utils.models import BaseModel, BaseModelWithHistory


class UnidadNegocio(BaseModel):
    """
    Unidad de negocio de la empresa.
    """
    codigo = models.CharField(verbose_name="código", max_length=12, unique=True)
    nombre = models.CharField(verbose_name="nombre", max_length=255)

    class Meta:
        verbose_name = "unidad de negocio"
        verbose_name_plural = "unidades de negocio"

    def __str__(self):
        return "{} - {}".format(self.codigo, self.nombre)


class Proyecto(BaseModelWithHistory):
    """
    Representa un proyecto de la empresa o Centro de Costo.

    """
    nombre = models.CharField("nombre", max_length=255, unique=True)
    codigo = models.CharField("código", max_length=15, unique=True)
    unidad_negocio = models.ForeignKey(UnidadNegocio, related_name="proyectos_de_la_unidad")
    perfil_tecnico = models.OneToOneField(PerfilTecnico, null=True, blank=True)

    # info
    contrato = models.CharField("contrato", max_length=255, blank=True, null=True)
    comitente = models.CharField("comitente", max_length=255, blank=True, null=True)
    lugar = models.CharField("lugar", max_length=255, blank=True, null=True)
    plazo = models.CharField("plazo", max_length=255, blank=True, null=True)
    fecha_inicio = models.DateField("fecha de inicio", blank=True, null=True)
    responsable = models.CharField("responsable", max_length=255, blank=True, null=True)
    cuit = models.CharField("CUIT", max_length=13, null=True, blank=True)

    fecha_baja = models.DateField("fecha de baja", null=True, blank=True)
    history = HistoricalRecords()

    objects = ProyectoManager()
    con_personas = ProyectoConPersonasManager()
    all_proyects = models.Manager()

    class Meta:
        verbose_name = "proyecto"
        verbose_name_plural = "proyectos"
        ordering = ['nombre', ]

    def clean(self):
        super(Proyecto, self).clean()
        if not self.pk and Proyecto.all_proyects.filter(nombre=self.nombre).exists():
            raise ValidationError({'nombre': ["Nombre de proyecto existente. Por favor, elija otro!",]})

    def __str__(self):
        return "{} - {}".format(self.codigo, self.nombre)

    @property
    def total_personas(self):
        return "{} personas".format(self.personas_involucradas.count())

    @property
    def activo(self):
        return self.fecha_baja is None


class CCT(BaseModelWithHistory):
    """
    Representa un Contrato Colectivo de Trabajo.

    """
    nombre = models.CharField("nombre", max_length=255, unique=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "CCT"
        verbose_name_plural = "CCTs"

    def __str__(self):
        return self.nombre

    @property
    def total_personas(self):
        return "{} personas".format(self.personas.count())



class Persona(BaseModelWithHistory):
    """
    Representa una persona que trabaja en la empresa.
    """
    legajo = models.IntegerField("legajo", unique=True)
    apellido = models.CharField("apellido", max_length=255)
    nombre = models.CharField("nombre", max_length=255)
    cuil = models.CharField("CUIL", max_length=15, unique=True)
    cct = models.ForeignKey(CCT, verbose_name="CCT", related_name="personas")
    proyecto = models.ForeignKey(Proyecto, verbose_name="proyecto",
                                 related_name="personas_involucradas")
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, unique=True, verbose_name="Usuario", null=True, blank=True, related_name="persona",
        help_text="Al asociar un usuario a la persona, este puede ingresar al sistema.")

    # tecnica
    observaciones = models.TextField(blank=True, null=True)
    funcion = models.ForeignKey(Funcion, null=True)
    desarraigo = models.BooleanField(default=False)
    fecha_ingreso = models.DateField("fecha de ingreso", blank=True, null=True)
    vto_carnet = models.DateField("registro de conducir", blank=True, null=True)
    vto_psicofisico = models.DateField("exámen psicofísico", blank=True, null=True)
    vto_cargagral = models.DateField("permiso carga general", blank=True, null=True)
    vto_cargapeligrosa = models.DateField("permiso carga peligrosa", blank=True, null=True)
    descripcion_vto1 = models.CharField("extra I", max_length=128, blank=True, null=True)
    descripcion_vto2 = models.CharField("extra II", max_length=128, blank=True, null=True)
    descripcion_vto3 = models.CharField("extra III", max_length=128, blank=True, null=True)
    vto_otros1 = models.DateField("fecha extra I", blank=True, null=True)
    vto_otros2 = models.DateField("fecha extra II", blank=True, null=True)
    vto_otros3 = models.DateField("fecha extra III", blank=True, null=True)

    # extras
    fecha_baja = models.DateField("fecha de baja", null=True, blank=True)
    history = HistoricalRecords()

    objects = PersonaManager()
    all_persons = models.Manager()

    class Meta:
        verbose_name = "persona"
        verbose_name_plural = "personas"
        ordering = ("apellido", "nombre", )

    def __str__(self):
        return "{} {}".format(self.apellido, self.nombre)

    def clean(self):
        super(Persona, self).clean()
        if not self.pk and Persona.all_persons.filter(legajo=self.legajo).exists():
            raise ValidationError({'legajo': ["Número de legajo ocupado.!",]})

    @property
    def activo(self):
        return self.fecha_baja is None