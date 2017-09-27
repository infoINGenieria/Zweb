# coding: utf-8
from rest_framework import serializers

from core.models import Obras
from presupuestos.models import (
    Presupuesto, Revision, ItemPresupuesto, TipoItemPresupuesto)


class TipoItemPresupuestoSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipoItemPresupuesto
        fields = ('pk', 'nombre')


class ItemPresupuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPresupuesto
        fields = ('tipo', 'pesos', 'dolares', 'observaciones')


class ObrasSerializer(serializers.ModelSerializer):
    unidad_negocio = serializers.CharField(source="unidad_negocio.codigo")

    class Meta:
        model = Obras
        fields = ('id', 'codigo', 'obra', 'lugar', 'plazo', 'responsable', 'unidad_negocio')


class PresupuestoSerializer(serializers.ModelSerializer):
    centro_costo = ObrasSerializer(read_only=True)
    vigente = serializers.IntegerField(source='revision_vigente.version', read_only=True)

    class Meta:
        model = Presupuesto
        fields = ('pk', 'centro_costo', 'fecha', 'aprobado', 'vigente')


class RevisionSerializer(serializers.ModelSerializer):
    items = ItemPresupuestoSerializer(many=True, read_only=True)
    presupuesto = PresupuestoSerializer(read_only=True)

    class Meta:
        model = Revision
        fields = ('pk', 'version', 'fecha', 'presupuesto', 'items')
