# -*- coding: utf-8 -*-
from django.db import models

from core.models import Obras
from costos.models import CostoTipo
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
        return self.centro_costo.mis_avances.filter(
            periodo__fecha_fin__lt=self.periodo.fecha_fin
        ).order_by("periodo__fecha_fin")

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


class ProyeccionCertificacion(BaseModel):
    centro_costo = models.ForeignKey(
        Obras, verbose_name="centro de costo", related_name="mis_proyecciones_certificacion",
        limit_choices_to={'es_cc':True})
    periodo = models.ForeignKey(Periodo, verbose_name="periodo de proyección")
    observacion = models.CharField(
        verbose_name='observación', max_length=255, null=True, blank=True)
    es_base = models.BooleanField(verbose_name="Es linea base", default=False)
    base_numero = models.PositiveSmallIntegerField(
        verbose_name='Base número', null=True, blank=True)

    class Meta:
        unique_together = ('periodo', 'centro_costo')
        verbose_name = 'proyeccion de certificación'
        verbose_name_plural = 'proyecciones de certificación'

    def __str__(self):
        return "Proyección de certificación de {} para {}".format(
            self.centro_costo, self.periodo)

    @property
    def total(self):
        return sum(self.items.values_list('monto', flat=True))

    @property
    def certificacion_real(self):
        return self.centro_costo.certificaciones_obras.filter(
            periodo__fecha_fin__lt=self.periodo.fecha_fin
        ).order_by("periodo__fecha_fin")


class ItemProyeccionCertificacion(BaseModel):
    proyeccion = models.ForeignKey(
        ProyeccionCertificacion, verbose_name='proyección', related_name='items'
    )
    periodo = models.ForeignKey(Periodo, verbose_name="periodo")
    monto = models.DecimalField(
        verbose_name="Monto ($)", max_digits=18, decimal_places=2)

    class Meta:
        verbose_name = 'item de proyección de certificación'
        verbose_name = 'ítemes de proyección de certificación'
        ordering = ('periodo__fecha_fin', )

    def __str__(self):
        return "Certificación de $ {:.1f} para {} en {}".format(
            self.monto, self.proyeccion.centro_costo, self.periodo)



class ProyeccionCosto(BaseModel):
    centro_costo = models.ForeignKey(
        Obras, verbose_name="centro de costo", related_name="mis_proyecciones_costos",
        limit_choices_to={'es_cc':True})
    periodo = models.ForeignKey(Periodo, verbose_name="periodo de proyección")
    observacion = models.CharField(
        verbose_name='observación', max_length=255, null=True, blank=True)
    es_base = models.BooleanField(verbose_name="Es linea base", default=False)
    base_numero = models.PositiveSmallIntegerField(
        verbose_name='Base número', null=True, blank=True)

    class Meta:
        unique_together = ('periodo', 'centro_costo')
        verbose_name = 'proyección de costo'
        verbose_name_plural = 'proyecciones de costo'

    def __str__(self):
        return "Proyección de costo de {} para {}".format(
            self.centro_costo, self.periodo)

    @property
    def costo_real(self):
        # todo!!!!!
        return []


class ItemProyeccionCosto(BaseModel):
    proyeccion = models.ForeignKey(
        ProyeccionCosto, verbose_name="proyección", related_name='items')
    periodo = models.ForeignKey(Periodo, verbose_name="periodo")
    tipo_costo = models.ForeignKey(CostoTipo, verbose_name="tipo de costo")
    monto = models.DecimalField(
        verbose_name="Monto ($)", max_digits=18, decimal_places=2)

    class Meta:
        verbose_name = 'item de proyección de costo'
        verbose_name = 'ítemes de proyección de costo'
        ordering = ('periodo__fecha_fin', )

    def __str__(self):
        return "{}: $ {:.1f} para {} en {}".format(
            self.tipo_costo, self.monto, self.proyeccion.centro_costo,
            self.periodo)
