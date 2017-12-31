# -*- coding: utf-8 -*-
from django.db import models

from core.models import Obras
from parametros.models import Periodo
from zweb_utils.models import BaseModel


class ProyeccionAvanceObra(BaseModel):
    centro_costo = models.ForeignKey(
        Obras, verbose_name="centro de costo", related_name="mis_proyecciones_avance",
        limit_choices_to={'es_cc':True})
    periodo = models.ForeignKey(Periodo, verbose_name="periodo de proyección")
    observacion = models.CharField(
        verbose_name='observación', max_length=255, null=True, blank=True)
    es_base = models.BooleanField(verbose_name="Es linea base", default=False)
    base_numero = models.PositiveSmallIntegerField(
        verbose_name='Base número', null=True, blank=True)

    class Meta:
        verbose_name = 'proyección de avance de obra'
        verbose_name_plural = 'proyecciones de avance de obra'
        unique_together = ('periodo', 'centro_costo', )

    def __str__(self):
        return "Proyección de avance de obra de {} para {}".format(
            self.centro_costo, self.periodo)

    @property
    def avance_real(self):
        return self.centro_costo.mis_avances.order_by("periodo__fecha_fin")

class ItemProyeccionAvanceObra(BaseModel):
    proyeccion = models.ForeignKey(
        ProyeccionAvanceObra, verbose_name='proyección', related_name='items'
    )
    periodo = models.ForeignKey(Periodo, verbose_name="periodo")
    avance = models.DecimalField(verbose_name='% de avance', decimal_places=3, max_digits=18)

    class Meta:
        verbose_name = 'item de proyección de avance de obra'
        verbose_name = 'ítemes de proyección de avance de obra'
        ordering = ('periodo__fecha_fin', )

    def __str__(self):
        return "{:.1f} % de avance para {} en {}".format(
            self.avance, self.proyeccion.centro_costo, self.periodo)
