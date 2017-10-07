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
        fields = ('pk', 'tipo', 'pesos', 'dolares', 'indirecto', 'observaciones')


class ObrasSerializer(serializers.ModelSerializer):
    unidad_negocio = serializers.CharField(source="unidad_negocio.codigo", read_only=True)

    class Meta:
        model = Obras
        fields = ('id', 'codigo', 'obra', 'lugar', 'plazo', 'responsable', 'unidad_negocio')


class PresupuestoSerializer(serializers.ModelSerializer):
    centro_costo = ObrasSerializer(read_only=True)
    centro_costo_id = serializers.IntegerField(source='centro_costo.pk')
    vigente = serializers.IntegerField(source='revision_vigente.version', read_only=True)

    class Meta:
        model = Presupuesto
        fields = ('pk', 'centro_costo', 'centro_costo_id', 'fecha', 'aprobado', 'vigente')

    def create(self, validated_data):
        import ipdb ; ipdb.set_trace()
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
                  'contingencia', 'estructura_no_ree', 'aval_por_anticipos',
                  'seguro_caucion', 'aval_por_cumplimiento_contrato',
                  'aval_por_cumplimiento_garantia', 'seguro_5', 'imprevistos',
                  'ganancias', 'impuestos_ganancias', 'sellado', 'ingresos_brutos',
                  'impuestos_cheque', 'costo_financiero', 'precio_venta',
                  'precio_venta_dolar', 'presupuesto', 'items')

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
        import ipdb ; ipdb.set_trace()
        items_data = validated_data.pop('items')
        presupuesto_data = validated_data.pop('presupuesto')

        instance.presupuesto.centro_costo_id = presupuesto_data.get('centro_costo_id', instance.presupuesto.centro_costo_id)
        instance.presupuesto.fecha = presupuesto_data.get('fecha', instance.presupuesto.fecha)
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
