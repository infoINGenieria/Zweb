# coding: utf-8
from django.db import models

from zweb_utils.models import BaseModel, BaseModelWithHistory


class UnidadNegocio(BaseModel):
    """
    Unidad de negocio de la empresa.
    """
    codigo = models.CharField(verbose_name="código", max_length=12, unique=True)
    nombre = models.CharField(verbose_name="nombre", max_length=255)
    activa = models.BooleanField(verbose_name='activa', default=True)
    observaciones = models.TextField()

    class Meta:
        verbose_name = "unidad de negocio"
        verbose_name_plural = "unidades de negocio"

    def __str__(self):
        return "{} - {}".format(self.codigo, self.nombre)
