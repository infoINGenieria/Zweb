# coding: utf-8
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework import serializers, status
from rest_framework.response import Response

from core.models import Obras, InfoObra
from costos.models import CostoTipo, AvanceObra, Costo
from presupuestos.models import (
    Presupuesto, Revision, ItemPresupuesto)
from registro.models import CertificacionItem, Certificacion, TableroControlOS
from parametros.models import Periodo
from proyecciones.models import (
    ProyeccionAvanceObra, ItemProyeccionAvanceObra,
    ProyeccionCertificacion, ItemProyeccionCertificacion,
    ProyeccionCosto, ItemProyeccionCosto)
from api.fields import Base64ImageField


class CostoTipoSerializer(serializers.ModelSerializer):

    class Meta:
        model = CostoTipo
        fields = ('pk', 'nombre')


class ItemPresupuestoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ItemPresupuesto
        fields = ('pk', 'tipo', 'pesos', 'dolares', 'indirecto', 'observaciones')


class InfoObraSerializer(serializers.ModelSerializer):

    class Meta:
        model = InfoObra
        fields = ('pk', 'cliente', 'gerente_proyecto', 'jefe_obra', 'planificador',
                  'control_gestion', 'inicio_comercial', 'inicio_contractual', 'inicio_real',
                  'plazo_comercial', 'plazo_contractual', 'plazo_con_ampliaciones',
                  'fin_previsto_comercial', 'fin_contractual', 'fin_contractual_con_ampliaciones')


class ObrasSerializer(serializers.ModelSerializer):
    unidad_negocio = serializers.CharField(source="unidad_negocio.codigo", read_only=True)
    info_obra = InfoObraSerializer(read_only=True)

    class Meta:
        model = Obras
        fields = ('id', 'codigo', 'obra', 'lugar', 'plazo', 'responsable',
                  'unidad_negocio', 'info_obra')


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
                  'impuestos_ganancias', 'sellado', 'ingresos_brutos',
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
        fields = ('pk', 'concepto', 'monto', 'observaciones')


class PeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = ('pk', 'descripcion', 'fecha_inicio', 'fecha_fin')


class ThinCertificacionSerializer(serializers.ModelSerializer):
    periodo_id = serializers.IntegerField(source='periodo.pk')
    centro_costo_id = serializers.IntegerField(source='obra.pk')

    class Meta:
        model = Certificacion
        fields = ('pk', 'periodo_id', 'centro_costo_id', 'total',)


class CertificacionSerializer(serializers.ModelSerializer):
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
        model = Certificacion
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


class ThinAvanceObraSerializer(serializers.ModelSerializer):
    periodo_id = serializers.IntegerField(source='periodo.pk')
    centro_costo_id = serializers.IntegerField(source='centro_costo.pk')

    class Meta:
        model = AvanceObra
        fields = ('pk', 'periodo_id', 'centro_costo_id', 'avance', 'observacion')


class AvanceObraSerializer(ThinAvanceObraSerializer):
    class Meta:
        model = AvanceObra
        fields = ('pk', 'periodo', 'periodo_id', 'centro_costo', 'centro_costo_id',
                  'avance', 'observacion')

    periodo = PeriodoSerializer(read_only=True)
    centro_costo = ObrasSerializer(read_only=True)

    def create(self, validated_data):
        centro_costo = validated_data.pop('centro_costo')
        periodo = validated_data.pop('periodo')
        avance = self.Meta.model(**validated_data)
        avance.centro_costo_id = centro_costo["pk"]
        avance.periodo_id = periodo["pk"]
        try:
            avance.save()
        except IntegrityError:
            raise serializers.ValidationError('%s existente' % self.Meta.model._meta.verbose_name)
        return avance

    def update(self, instance, validated_data):
        centro_costo = validated_data.pop('centro_costo')
        periodo = validated_data.pop('periodo')
        instance.centro_costo_id = centro_costo.get('pk', instance.centro_costo_id)
        instance.periodo_id = periodo.get('pk', instance.periodo)
        instance.avance = validated_data.get("avance", instance.avance)
        instance.observacion = validated_data.get("observacion", instance.observacion)
        instance.save()
        return instance


class ItemProyeccionAvanceObraSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = ItemProyeccionAvanceObra
        fields = ('pk', 'periodo', 'avance')


class ProyeccionAvanceObraSerializer(serializers.ModelSerializer):
    periodo = PeriodoSerializer(read_only=True)
    periodo_id = serializers.IntegerField(source='periodo.pk')
    centro_costo = ObrasSerializer(read_only=True)
    centro_costo_id = serializers.IntegerField(source='centro_costo.pk')
    items = ItemProyeccionAvanceObraSerializer(many=True)
    avance_real = ThinAvanceObraSerializer(many=True, read_only=True)
    base_vigente = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProyeccionAvanceObra
        fields = ('pk', 'periodo', 'periodo_id', 'centro_costo', 'centro_costo_id',
                  'observacion', 'es_base', 'base_numero', 'items', 'avance_real',
                  'base_vigente')

    def create(self, validated_data):
        centro_costo = validated_data.pop('centro_costo')
        periodo = validated_data.pop('periodo')
        items = validated_data.pop('items')
        avance = ProyeccionAvanceObra(**validated_data)
        avance.centro_costo_id = centro_costo["pk"]
        avance.periodo_id = periodo["pk"]
        if not ProyeccionAvanceObra.objects.filter(
                centro_costo_id=avance.centro_costo_id).exists():
            avance.base_numero = 0
            avance.es_base = True

        try:
            avance.save()
        except ValidationError as e:
            raise serializers.ValidationError(e.message)

        for item_data in items:
            ItemProyeccionAvanceObra.objects.create(
                proyeccion=avance,
                periodo=item_data["periodo"],
                avance=item_data["avance"]
            )
        return avance

    def update(self, instance, validated_data):
        centro_costo = validated_data.pop('centro_costo')
        periodo = validated_data.pop('periodo')
        items = validated_data.pop('items')
        instance.centro_costo_id = centro_costo.get('pk', instance.centro_costo_id)
        instance.periodo_id = periodo.get('pk', instance.periodo)
        instance.observacion = validated_data.get("observacion", instance.observacion)
        instance.es_base = validated_data.get("es_base", instance.es_base)
        instance.base_numero = validated_data.get("base_numero", instance.base_numero)
        try:
            instance.save()
        except ValidationError as e:
            raise serializers.ValidationError(e.message)

        exists_pks = []
        for item in items:
            if "pk" in item:
                pk = item.pop('pk')
                exists_pks.append(pk)
                item_obj, _ = ItemProyeccionAvanceObra.objects.update_or_create(
                    pk=pk, proyeccion=instance, defaults={
                        'periodo': item.get('periodo'),
                        'avance': item.get("avance")
                    })
            else:
                item_obj = ItemProyeccionAvanceObra(
                    proyeccion=instance,
                    periodo=item.get('periodo'),
                    avance=item.get('avance'))
                item_obj.save()
                exists_pks.append(item_obj.pk)
        # eliminar items no enviados
        instance.items.exclude(pk__in=exists_pks).delete()
        return instance


class ItemProyeccionCertificacionSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = ItemProyeccionCertificacion
        fields = ('pk', 'periodo', 'monto')


class ProyeccionCertificacionSerializer(serializers.ModelSerializer):
    periodo = PeriodoSerializer(read_only=True)
    periodo_id = serializers.IntegerField(source='periodo.pk')
    centro_costo = ObrasSerializer(read_only=True)
    centro_costo_id = serializers.IntegerField(source='centro_costo.pk')
    items = ItemProyeccionCertificacionSerializer(many=True)
    certificacion_real = ThinCertificacionSerializer(many=True, read_only=True)

    base_vigente = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProyeccionAvanceObra
        fields = ('pk', 'periodo', 'periodo_id', 'centro_costo', 'centro_costo_id',
                  'observacion', 'es_base', 'base_numero', 'items', 'certificacion_real',
                  'base_vigente')


    def create(self, validated_data):
        centro_costo = validated_data.pop('centro_costo')
        periodo = validated_data.pop('periodo')
        items = validated_data.pop('items')
        certificacion = ProyeccionCertificacion(**validated_data)
        certificacion.centro_costo_id = centro_costo["pk"]
        certificacion.periodo_id = periodo["pk"]
        if not ProyeccionCertificacion.objects.filter(
                centro_costo_id=certificacion.centro_costo_id).exists():
            certificacion.base_numero = 0
            certificacion.es_base = True
        try:
            certificacion.save()
        except ValidationError as e:
            raise serializers.ValidationError(e.message)
        for item_data in items:
            ItemProyeccionCertificacion.objects.create(
                proyeccion=certificacion,
                periodo=item_data["periodo"],
                monto=item_data["monto"]
            )
        return certificacion

    def update(self, instance, validated_data):
        centro_costo = validated_data.pop('centro_costo')
        periodo = validated_data.pop('periodo')
        items = validated_data.pop('items')
        instance.centro_costo_id = centro_costo.get('pk', instance.centro_costo_id)
        instance.periodo_id = periodo.get('pk', instance.periodo)
        instance.observacion = validated_data.get("observacion", instance.observacion)
        instance.es_base = validated_data.get("es_base", instance.es_base)
        instance.base_numero = validated_data.get("base_numero", instance.base_numero)
        try:
            instance.save()
        except ValidationError as e:
            raise serializers.ValidationError(e.message)
        exists_pks = []
        for item in items:
            if "pk" in item:
                pk = item.pop('pk')
                exists_pks.append(pk)
                item_obj, _ = ItemProyeccionCertificacion.objects.update_or_create(
                    pk=pk, proyeccion=instance, defaults={
                        'periodo': item.get('periodo'),
                        'monto': item.get("monto")
                    })
            else:
                item_obj = ItemProyeccionCertificacion(
                    proyeccion=instance,
                    periodo=item.get('periodo'),
                    monto=item.get('monto'))
                item_obj.save()
                exists_pks.append(item_obj.pk)
        # eliminar items no enviados
        instance.items.exclude(pk__in=exists_pks).delete()
        return instance



class ThinCostoSerializer(serializers.ModelSerializer):
    periodo_id = serializers.IntegerField(source='periodo.pk')
    centro_costo_id = serializers.IntegerField(source='centro_costo.pk')
    tipo_costo_id = serializers.IntegerField(source='tipo_costo.pk')

    class Meta:
        model = Costo
        fields = ('pk', 'periodo_id', 'centro_costo_id',
                  'tipo_costo_id', 'monto_total', 'observacion')


class ItemProyeccionCostoSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = ItemProyeccionCosto
        fields = ('pk', 'periodo', 'tipo_costo', 'monto')


class ProyeccionCostoSerializer(serializers.ModelSerializer):
    periodo = PeriodoSerializer(read_only=True)
    periodo_id = serializers.IntegerField(source='periodo.pk')
    centro_costo = ObrasSerializer(read_only=True)
    centro_costo_id = serializers.IntegerField(source='centro_costo.pk')

    items = ItemProyeccionCostoSerializer(many=True)
    costo_real = ThinCostoSerializer(many=True, read_only=True)

    periodos = serializers.SerializerMethodField()
    base_vigente = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProyeccionCosto
        fields = ('pk', 'periodo', 'periodo_id', 'centro_costo', 'centro_costo_id',
                  'observacion', 'es_base', 'base_vigente',
                  'base_numero', 'items', 'costo_real', 'periodos')

    def get_periodos(self, obj):
        return obj.items.values_list(
            'periodo__id', flat=True).distinct().order_by(
                'periodo__fecha_fin')

    def create(self, validated_data):
        centro_costo = validated_data.pop('centro_costo')
        periodo = validated_data.pop('periodo')
        items = validated_data.pop('items')
        costo = ProyeccionCosto(**validated_data)
        costo.centro_costo_id = centro_costo["pk"]
        costo.periodo_id = periodo["pk"]
        if not ProyeccionCosto.objects.filter(
                centro_costo_id=costo.centro_costo_id).exists():
            costo.base_numero = 0
            costo.es_base = True
        try:
            costo.save()
        except ValidationError as e:
            raise serializers.ValidationError(e.message)
        for item_data in items:
            ItemProyeccionCosto.objects.create(
                proyeccion=costo,
                periodo=item_data["periodo"],
                tipo_costo=item_data["tipo_costo"],
                monto=item_data["monto"]
            )
        return costo

    def update(self, instance, validated_data):
        centro_costo = validated_data.pop('centro_costo')
        periodo = validated_data.pop('periodo')
        items = validated_data.pop('items')
        instance.centro_costo_id = centro_costo.get('pk', instance.centro_costo_id)
        instance.periodo_id = periodo.get('pk', instance.periodo)
        instance.observacion = validated_data.get("observacion", instance.observacion)
        instance.es_base = validated_data.get("es_base", instance.es_base)
        instance.base_numero = validated_data.get("base_numero", instance.base_numero)
        try:
            instance.save()
        except ValidationError as e:
            raise serializers.ValidationError(e.message)
        exists_pks = []
        for item in items:
            if "pk" in item:
                pk = item.pop('pk')
                exists_pks.append(pk)
                item_obj, _ = ItemProyeccionCosto.objects.update_or_create(
                    pk=pk, proyeccion=instance, defaults={
                        'periodo': item.get('periodo'),
                        'tipo_costo': item.get('tipo_costo'),
                        'monto': item.get("monto")
                    })
            else:
                item_obj = ItemProyeccionCosto(
                    proyeccion=instance,
                    periodo=item.get('periodo'),
                    tipo_costo=item.get('tipo_costo'),
                    monto=item.get('monto'))
                item_obj.save()
                exists_pks.append(item_obj.pk)
        # eliminar items no enviados
        instance.items.exclude(pk__in=exists_pks).delete()
        return instance



class TableroControlOSSerializer(serializers.ModelSerializer):
    periodo = PeriodoSerializer(read_only=True)
    periodo_id = serializers.IntegerField(source='periodo.pk')
    obra = ObrasSerializer(read_only=True)
    obra_id = serializers.IntegerField(source='obra.pk')
    user = serializers.CharField(source='user.username', read_only=True)

    consolidado_img = Base64ImageField()
    certificacion_img = Base64ImageField()
    costos_img = Base64ImageField()
    avance_img = Base64ImageField()
    resultado_img = Base64ImageField(required=False)

    pdf = serializers.FileField(read_only=True)

    class Meta:
        model = TableroControlOS
        fields = ('pk', 'user', 'obra', 'obra_id', 'periodo', 'periodo_id', 'pdf', 'comentario',
                  'info_obra', 'revisiones_historico', 'tablero_data', 'consolidado_data',
                  'certificacion_data', 'costos_data', 'avance_data', 'resultados_data',
                  'tablero_html', 'consolidado_img', 'certificacion_img', 'costos_img',
                  'avance_img', 'resultado_img')

    def create(self, validated_data):
        centro_costo = validated_data.pop('obra')
        periodo = validated_data.pop('periodo')

        tablero = TableroControlOS(**validated_data)
        tablero.obra_id = centro_costo["pk"]
        tablero.periodo_id = periodo["pk"]
        tablero.user = self.context["request"].user
        tablero.generate_pdf(self.context["request"])
        tablero.save()
        return tablero
