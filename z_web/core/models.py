from __future__ import unicode_literals

from django.db import models
from django.conf import settings

from parametros.models import FamiliaEquipo, Funcion


class Equipos(models.Model):
    """
    Equipos y maquinarias de la empresa.
    En futuras versiones debería ser movido a taller.
    """
    id = models.AutoField(db_column='ID', primary_key=True)
    n_interno = models.CharField(verbose_name='n° interno', db_column='N_INTERNO', max_length=255, blank=True, null=True)
    equipo = models.CharField(verbose_name='tipo de equipo', db_column='EQUIPO', max_length=255, blank=True, null=True)
    marca = models.CharField(verbose_name='marca', db_column='MARCA', max_length=255, blank=True, null=True)
    modelo = models.CharField(verbose_name='modelo', db_column='MODELO', max_length=255, blank=True, null=True)
    año = models.FloatField(verbose_name='año', db_column='AÑO', blank=True, null=True)
    dominio = models.CharField(verbose_name='dominio', db_column='DOMINIO', max_length=255, blank=True, null=True)
    nro_serie = models.CharField(verbose_name="n° serie", max_length=255, blank=True, null=True)
    vto_vtv = models.DateField(verbose_name='vto VTV', db_column='VTO_VTV', blank=True, null=True)
    vto_seguro = models.DateField(verbose_name='vto seguro', db_column='VTO_SEGURO', blank=True, null=True)
    vto_ruta = models.DateField(verbose_name='vto ruta', null=True, blank=True)
    vto_certificacion = models.DateField(verbose_name='vto certificación', null=True, blank=True)
    vto_certificacion_obs = models.CharField(verbose_name='observación vto. certificación', max_length=255, blank=True, null=True)
    descripcion_vto1 = models.CharField(verbose_name='descripción vto1', db_column='DESCRIPCION_VTO1', max_length=128, blank=True, null=True)
    descripcion_vto2 = models.CharField(verbose_name='descripción vto2', db_column='DESCRIPCION_VTO2', max_length=128, blank=True, null=True)
    descripcion_vto3 = models.CharField(verbose_name='descripción vto3', db_column='DESCRIPCION_VTO3', max_length=128, blank=True, null=True)
    vto_otros1 = models.DateField(verbose_name='fecha vto1', db_column='VTO_OTROS1', blank=True, null=True)
    vto_otros2 = models.DateField(verbose_name='fecha vto2', db_column='VTO_OTROS2', blank=True, null=True)
    vto_otros3 = models.DateField(verbose_name='fecha vto3', db_column='VTO_OTROS3', blank=True, null=True)
    familia_equipo = models.ForeignKey(FamiliaEquipo, db_column='FAMILIA_EQUIPO_ID', blank=True, null=True)

    class Meta:
        verbose_name = "equipo"
        verbose_name_plural = "equipos"
        db_table = 'equipos'

    def __str__(self):
        return "{} - {}".format(self.n_interno, self.equipo)


class EstServicio(models.Model):
    """
    OK
    """
    id = models.AutoField(db_column='ID', primary_key=True)
    nombre = models.CharField(db_column='NOMBRE', max_length=128)

    class Meta:
        verbose_name = "estación de servicio"
        verbose_name_plural = "estaciones de servicio"
        db_table = 'est_servicio'

    def __str__(self):
        return self.nombre


class FrancoLicencia(models.Model):
    """
    OK
    """
    id = models.AutoField(db_column='ID', primary_key=True)
    operario = models.ForeignKey('Operarios', db_column='OPERARIO_ID')
    ajuste_francos = models.IntegerField(db_column='AJUSTE_FRANCOS')
    ajuste_licencias = models.IntegerField(db_column='AJUSTE_LICENCIAS')
    pagados = models.IntegerField(db_column='PAGADOS')
    solicitados1 = models.IntegerField(db_column='SOLICITADOS1', blank=True, null=True)
    solicitados2 = models.IntegerField(db_column='SOLICITADOS2', blank=True, null=True)
    entra1 = models.DateField(db_column='ENTRA1', blank=True, null=True)
    entra2 = models.DateField(db_column='ENTRA2', blank=True, null=True)
    sale1 = models.DateField(db_column='SALE1', blank=True, null=True)
    sale2 = models.DateField(db_column='SALE2', blank=True, null=True)

    class Meta:
        verbose_name = "franco y licencia"
        verbose_name_plural = "francos y licencias"
        db_table = 'franco_licencia'

    def __str__(self):
        return "Francos y Licencias de {}".format(self.operario.nombre)


class Obras(models.Model):
    """
    Una obra representa una unidad integradora de recursos (equipos, personas, etc).
    En algunos casos, una obra es un Centro de costos, la cual engloba los calculos de costos asociados a un CC.
    Se identifican con es_cc = True
    También se le llama proyecto.
    Eventualmente, habría que refactorizar este modelo.
    """
    id = models.AutoField(db_column='ID', primary_key=True)
    codigo = models.CharField(db_column='CODIGO', max_length=255, unique=True)
    obra = models.CharField(db_column='OBRA', max_length=255, blank=True, null=True)
    contrato = models.CharField(db_column='CONTRATO', max_length=64, blank=True, null=True)
    comitente = models.CharField(db_column='COMITENTE', max_length=255, blank=True, null=True)
    cuit = models.CharField(db_column='CUIT', max_length=255, blank=True, null=True)
    lugar = models.CharField(db_column='LUGAR', max_length=255, blank=True, null=True)
    plazo = models.CharField(db_column='PLAZO', max_length=255, blank=True, null=True)
    fecha_inicio = models.DateField(db_column='FECHA_INICIO', blank=True, null=True)
    fecha_fin = models.DateField(verbose_name="Fecha de finalización", blank=True, null=True,
                                 help_text="Si está establecido, esta obra o CC no será mostrado en listas "
                                           "desplegables (se considera inactiva).")
    responsable = models.CharField(db_column='RESPONSABLE', max_length=255, blank=True, null=True)
    tiene_comida = models.BooleanField(db_column='TIENE_COMIDA', default=True)
    tiene_vianda = models.BooleanField(db_column='TIENE_VIANDA', default=True)
    tiene_desarraigo = models.BooleanField(db_column='TIENE_DESARRAIGO', default=True)
    limite_vianda_doble = models.FloatField(db_column='LIMITE_VIANDA_DOBLE', default=2)
    tiene_registro = models.BooleanField(db_column='TIENE_REGISTRO', default=True)
    tiene_equipo = models.BooleanField(db_column='TIENE_EQUIPO', default=True)
    descuenta_francos = models.BooleanField(verbose_name="Se utiliza para francos", db_column='DESCUENTA_FRANCOS', default=False)
    descuenta_licencias = models.BooleanField(verbose_name="Se utiliza para licencias anuales", db_column='DESCUENTA_LICENCIAS', default=False)
    es_cc = models.BooleanField(verbose_name="Tratar como CC", default=False,
                                help_text="Si está seleccionada, la obra es considerada un Centro de Costos (CC)")
    prorratea_costos = models.BooleanField(verbose_name="¿Prorratea Costos?", default=False,
                                           help_text="Si está seleccionada, los costos se prorratean en los demás CC")

    unidad_negocio = models.ForeignKey(
        'organizacion.UnidadNegocio', verbose_name='unidad de negocio', null=True)

    class Meta:
        verbose_name = "obra"
        verbose_name_plural = "obras"
        db_table = 'obras'

    def __str__(self):
        return "{} - {}".format(self.codigo, self.obra)

    @property
    def esta_activa(self):
        return self.fecha_fin is None

    @classmethod
    def get_centro_costos(cls, user):
        obra_qs = Obras.objects.filter(es_cc=True)
        try:
            if user.extension.unidad_negocio:
                obra_qs = obra_qs.filter(unidad_negocio=user.extension.unidad_negocio)
        except UserExtension.DoesNotExist:
            pass
        return obra_qs

    @classmethod
    def get_centro_costos_ms(cls):
        return Obras.objects.filter(
            es_cc=True, unidad_negocio__codigo='MS')



class CCT(models.Model):
    """
    Representa un Contrato Colectivo de Trabajo.

    """
    nombre = models.CharField("nombre", max_length=255, unique=True)

    class Meta:
        verbose_name = "CCT"
        verbose_name_plural = "CCTs"

    def __str__(self):
        return self.nombre

    @property
    def total_personas(self):
        return "{} personas".format(self.operarios.count())


class Operarios(models.Model):
    """
    OK
    """
    id = models.AutoField(db_column='ID', primary_key=True)
    n_legajo = models.CharField(db_column='N_LEGAJO', max_length=255, blank=True, null=True)
    nombre = models.CharField(db_column='NOMBRE', max_length=255, blank=True, null=True)
    cuil = models.CharField(db_column='CUIL', max_length=255, blank=True, null=True)
    observaciones = models.TextField(db_column='OBSERVACIONES', max_length=255, blank=True, null=True)
    funcion = models.ForeignKey(Funcion, db_column='FUNCION')
    desarraigo = models.BooleanField(db_column='DESARRAIGO', default=False)
    fecha_ingreso = models.DateField(db_column='FECHA_INGRESO', blank=True, null=True)
    vto_carnet = models.DateField(db_column='VTO_CARNET', blank=True, null=True)
    vto_psicofisico = models.DateField(db_column='VTO_PSICOFISICO', blank=True, null=True)
    vto_cargagral = models.DateField(db_column='VTO_CARGAGRAL', blank=True, null=True)
    vto_cargapeligrosa = models.DateField(db_column='VTO_CARGAPELIGROSA', blank=True, null=True)
    descripcion_vto1 = models.CharField(db_column='DESCRIPCION_VTO1', max_length=128, blank=True, null=True)
    descripcion_vto2 = models.CharField(db_column='DESCRIPCION_VTO2', max_length=128, blank=True, null=True)
    descripcion_vto3 = models.CharField(db_column='DESCRIPCION_VTO3', max_length=128, blank=True, null=True)
    vto_otros1 = models.DateField(db_column='VTO_OTROS1', blank=True, null=True)
    vto_otros2 = models.DateField(db_column='VTO_OTROS2', blank=True, null=True)
    vto_otros3 = models.DateField(db_column='VTO_OTROS3', blank=True, null=True)

    cct = models.ForeignKey(CCT, verbose_name="CCT", related_name="operarios", null=True)

    class Meta:
        verbose_name = "operario"
        verbose_name_plural = "operarios"
        db_table = 'operarios'

    def __str__(self):
        return "{} ({})".format(self.nombre, self.n_legajo)


class Usuario(models.Model):
    """
    OK
    """
    ROL = (
        ("De carga", "De carga"),
        ("Administrador", "Administrador"),
    )
    id = models.AutoField(db_column='ID', primary_key=True)
    user = models.CharField(db_column='USER', max_length=16)
    pass_field = models.CharField(db_column='PASS', max_length=128)
    rol = models.CharField(db_column='ROL', max_length=128, choices=ROL)
    fechabaja = models.DateTimeField(
            db_column='FECHABAJA', blank=True, null=True, verbose_name="Fecha de baja",
            help_text="Si la fecha de baja no está establecida, el usuario está activo.")

    class Meta:
        verbose_name = "usuario de ZProjects"
        verbose_name_plural = "usuarios de ZProjects"
        db_table = 'usuario'

    def __str__(self):
        return self.user


class UserExtension(models.Model):
    """
    Modelo para almacenar información relativa al usuario
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='extension')
    unidad_negocio = models.ForeignKey(
        'organizacion.UnidadNegocio', verbose_name='unidad de negocio', null=True)

    class Meta:
        verbose_name = 'información adicional'
        verbose_name_plural = 'información adicional'

    def __str__(self):
        return "información de {}".format(self.user)
