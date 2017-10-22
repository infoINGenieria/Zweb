# coding: utf-8
from django.db.utils import IntegrityError
from rest_framework import serializers, status
from rest_framework.response import Response

from core.models import Obras
from presupuestos.models import (
    Presupuesto, Revision, ItemPresupuesto, TipoItemPresupuesto)
from registro.models import CertificacionItem, CertificacionReal, CertificacionProyeccion
from parametros.models import Periodo


class TipoItemPresupuestoSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipoItemPresupuesto
        fields = ('pk', 'nombre')


class ItemPresupuestoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ItemPresupuesto
        fields = ('pk', 'tipo', 'pesos', 'dolares', 'indirecto', 'observaciones')


class ObrasSerializer(serializers.ModelSerializer):
    unidad_negocio = serializers.CharField(source="unidad_negocio.codigo", read_only=True)

    class Meta:
        model = Obras
        fields = ('id', 'codigo', 'obra', 'lugar', 'plazo', 'responsable', 'unidad_negocio')


class PresupuestoSerializer(serializers.ModelSerializer):
    centro_costo = ObrasSerializer(read_only=True)
    centro_costo_id = serializers.IntegerField(source='centro_costo.pk')
    versiones = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=100), read_only=True)
    vigente = serializers.IntegerField(source='revision_vigente.version', read_only=True)
    venta_actual = serializers.DecimalField(
        max_digits=18, decimal_places=2, read_only=True)
    venta_revision_anterior = serializers.DecimalField(
        max_digits=18, decimal_places=2, read_only=True)
    fecha_vigente = serializers.DateField(read_only=True)

    class Meta:
        model = Presupuesto
        fields = ('pk', 'centro_costo', 'centro_costo_id', 'fecha', 'aprobado',
                  'vigente', 'fecha_vigente', 'venta_actual', 'venta_revision_anterior',
                  'versiones')

    def create(self, validated_data):
        centro = validated_data.pop('centro_costo')
        presupuesto = Presupuesto(**validated_data)
        presupuesto.centro_costo_id = centro["pk"]
        presupuesto.save()
        return presupuesto

class RevisionSerializer(serializers.ModelSerializer):
    items = ItemPresupuestoSerializer(many=True)
    presupuesto = PresupuestoSerializer()

    class Meta:
        model = Revision
        fields = ('pk', 'version', 'fecha', 'valor_dolar',
                  'venta_contractual_b0', 'ordenes_cambio', 'reajustes_precio',
                  'reclamos_reconocidos',
                  'contingencia', 'estructura_no_ree', 'aval_por_anticipos',
                  'seguro_caucion', 'aval_por_cumplimiento_contrato',
                  'aval_por_cumplimiento_garantia', 'seguro_5', 'imprevistos',
                  'ganancias', 'impuestos_ganancias', 'sellado', 'ingresos_brutos',
                  'impuestos_cheque', 'costo_financiero', 'presupuesto', 'items')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        presupuesto = validated_data.pop('presupuesto')
        revision = Revision(**validated_data)
        revision.presupuesto = presupuesto
        revision.save()
        for item_data in items_data:
            ItemPresupuesto.objects.create(revision=revision, **item_data)
        return revision

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')
        presupuesto_data = validated_data.pop('presupuesto')

        instance.presupuesto.centro_costo_id = presupuesto_data.get('centro_costo_id', instance.presupuesto.centro_costo_id)
        instance.presupuesto.aprobado = presupuesto_data.get('aprobado', instance.presupuesto.aprobado)

        for attr in validated_data.keys():
            setattr(instance, attr, validated_data.get(attr, getattr(instance, attr)))
        instance.save()
        instance.presupuesto.save()

        instance.items.all().delete()
        for item in items_data:
            ItemPresupuesto.objects.create(revision=instance, **item)
        # actualizar, crear y borrar items
        return instance

class CertificacionItemSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = CertificacionItem
        fields = ('pk', 'descripcion', 'monto', 'adicional')


class PeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = ('pk', 'descripcion', 'fecha_inicio', 'fecha_fin')


class CertificacionRealSerializer(serializers.ModelSerializer):
    periodo = PeriodoSerializer(read_only=True)
    periodo_id = serializers.IntegerField(source='periodo.pk')
    obra = ObrasSerializer(read_only=True)
    obra_id = serializers.IntegerField(source='obra.pk')
    items = CertificacionItemSerializer(many=True)
    total = serializers.DecimalField(
        max_digits=18, decimal_places=2, read_only=True)
    total_sin_adicional = serializers.DecimalField(
        max_digits=18, decimal_places=2, read_only=True)
    total_adicional = serializers.DecimalField(
        max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = CertificacionReal
        fields = ('pk', 'periodo', 'periodo_id', 'obra', 'obra_id', 'items', 'total',
                  'total_sin_adicional', 'total_adicional')

    def create(self, validated_data):
        obra = validated_data.pop('obra')
        periodo = validated_data.pop('periodo')
        items = validated_data.pop('items')
        certif = self.Meta.model(**validated_data)
        certif.obra_id = obra["pk"]
        certif.periodo_id = periodo["pk"]
        try:
            certif.save()
        except IntegrityError:
            raise serializers.ValidationError('%s existente' % self.Meta.model._meta.verbose_name)
        for item_data in items:
            CertificacionItem.objects.create(certificacion=certif, **item_data)
        return certif

    def update(self, instance, validated_data):
        obra = validated_data.pop('obra')
        periodo = validated_data.pop('periodo')
        items = validated_data.pop('items')
        instance.obra_id = obra.get('pk', instance.obra_id)
        instance.periodo_id = periodo.get('pk', instance.periodo)
        instance.save()

        exists_pks = []
        for item in items:
            if "pk" in item:
                pk = item.pop('pk')
                exists_pks.append(pk)
                item_obj, _ = CertificacionItem.objects.update_or_create(pk=pk, certificacion=instance, defaults=item)
            else:
                item_obj = CertificacionItem(certificacion=instance, **item)
                item_obj.save()
                exists_pks.append(item_obj.pk)
        # eliminar items no enviados
        instance.items.exclude(pk__in=exists_pks).delete()
        return instance

class CertificacionProyeccionSerializer(CertificacionRealSerializer):

    class Meta:
        model = CertificacionProyeccion
        fields = ('pk', 'periodo', 'periodo_id', 'obra', 'obra_id', 'items', 'total',
                  'total_sin_adicional', 'total_adicional')
