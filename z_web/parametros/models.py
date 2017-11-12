from django.db import models
from django.utils.text import slugify

from model_utils.managers import QueryManager


class FamiliaEquipo(models.Model):
    nombre = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "familia de equipo"
        verbose_name_plural = "familias de equipo"
        db_table = 'familia_equipo'

    def __str__(self):
        return self.nombre


class Funcion(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    funcion = models.CharField(db_column='FUNCION', unique=True, max_length=128)

    class Meta:
        verbose_name = "función"
        verbose_name_plural = "funciones"
        db_table = 'funcion'

    def __str__(self):
        return self.funcion


class Parametro(models.Model):
    clave = models.CharField(db_column='CLAVE', primary_key=True, max_length=45)
    clave_grupo = models.CharField(db_column='CLAVE_GRUPO', max_length=45, blank=True, null=True)
    valor = models.CharField(db_column='VALOR', max_length=128, blank=True, null=True)

    class Meta:
        verbose_name = "parametro del sistema"
        verbose_name_plural = "parametros del sistema"
        db_table = 'parametro'

    def __str__(self):
        return "{}({}) - {}".format(self.clave, self.clave_grupo, self.valor)


class Situacion(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    situacion = models.CharField(db_column='SITUACION', max_length=128)

    class Meta:
        verbose_name = "situación"
        verbose_name_plural = "situaciones"
        db_table = 'situacion'

    def __str__(self):
        return self.situacion


class TipoCosto(models.Model):
    nombre = models.CharField(max_length=255, blank=True, null=True)
    tipo = models.IntegerField(unique=True)

    class Meta:
        verbose_name = "tipo de costo"
        verbose_name_plural = "tipos de costo"
        db_table = 'tipo_costo'

    def __str__(self):
        return "{} ({})".format(self.nombre, self.tipo)


class Periodo(models.Model):
    descripcion = models.CharField(verbose_name="Periodo", max_length=255)
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de cierre")

    objects = models.Manager()
    con_parametros_costos = QueryManager(parametros_costos__isnull=False)

    class Meta:
        verbose_name = 'periodo'
        verbose_name_plural = 'periodos'
        ordering = ['-fecha_fin', ]

    def __str__(self):
        return "{}".format(self.descripcion)

    @property
    def key(self):
        return slugify(self.descripcion)

    def save(self, *args, **kwargs):
        parametro = None
        if not self.pk:
            from costos.models import CostoParametro
            ultimo = CostoParametro.objects.latest("periodo__fecha_fin")
            parametro = CostoParametro(pesos_usd=ultimo.pesos_usd, precio_go=ultimo.precio_go)
        super(Periodo, self).save(*args, **kwargs)
        if parametro:
            parametro.periodo = self
            parametro.save()
