# coding: utf-8
from decimal import Decimal as D
from django.db.utils import IntegrityError
from django.db.transaction import atomic
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from rest_framework import serializers, status, exceptions
from rest_framework.response import Response

from core.models import Obras, InfoObra, Equipos
from costos.models import CostoTipo, AvanceObra, Costo
from equipos.models import (
    ParametrosGenerales, AsistenciaEquipo, RegistroAsistenciaEquipo,
    LubricantesValores, TrenRodajeValores, PosesionValores,
    ReparacionesValores, CostoEquipoValores, LubricanteItem,
    LubricantesParametrosItem, LubricantesValoresItem,
    LubricantesParametros, TrenRodajeParametros,
    PosesionParametros, PosesionValores,
    ReparacionesParametros, ReparacionesValores,
    ManoObraValores, EquipoAlquiladoValores
)
from equipos.tasks import copy_cost_structure
from presupuestos.models import (
    Presupuesto, Revision, ItemPresupuesto)
from registro.models import CertificacionItem, Certificacion, TableroControlOS
from parametros.models import Periodo, FamiliaEquipo
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
        fields = ('id', 'codigo', 'obra', 'deposito', 'lugar', 'plazo', 'responsable',
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


################
##   TALLER   ##
################

class FamiliaEquipoSerializer(serializers.ModelSerializer):

    class Meta:
        model = FamiliaEquipo
        fields = ('pk', 'nombre', )


class EquipoSerializer(serializers.ModelSerializer):
    familia_equipo = FamiliaEquipoSerializer(read_only=True)
    anio = serializers.IntegerField(source='año')
    familia_equipo_id = serializers.IntegerField(source='familia_equipo.pk')
    fecha_baja = serializers.DateField(read_only=True)

    copy_costo_from = serializers.IntegerField(required=False)

    class Meta:
        model = Equipos
        fields = (
            'id', 'n_interno', 'equipo', 'marca', 'modelo',
            'anio', 'dominio', 'nro_serie', 'familia_equipo',
            'familia_equipo_id', 'es_alquilado', 'fecha_baja',
            'excluir_costos_taller', 'implica_mo_logistica',
            'copy_costo_from'
        )

    def create(self, validated_data):
        familia_equipo = validated_data.pop('familia_equipo')
        copy_costo_from = validated_data.pop('copy_costo_from')
        equipo = Equipos(**validated_data)
        equipo.familia_equipo_id = familia_equipo["pk"]
        equipo.save()
        copy_cost_structure(equipo.pk, copy_costo_from)
        return equipo

    def update(self, instance, validated_data):
        familia_equipo = validated_data.pop('familia_equipo')
        for attr in validated_data.keys():
            setattr(instance, attr, validated_data.get(attr, getattr(instance, attr)))
        instance.familia_equipo_id = familia_equipo.get('pk', instance.familia_equipo_id)
        instance.save()
        return instance


class ParametrosGeneralesTallerSerializer(serializers.ModelSerializer):
    valido_desde = PeriodoSerializer(read_only=True)
    valido_desde_id = serializers.IntegerField(source='valido_desde.pk')

    class Meta:
        model = ParametrosGenerales
        fields = (
            'pk', 'valido_desde', 'valido_desde_id', 'consumo_equipo_viales', 'consumo_equipo_automotor',
            'precio_gasoil', 'precio_lubricante', 'precio_hidraulico',
            'horas_por_dia', 'dias_por_mes', 'horas_trabajo_anio', 'valor_dolar'
        )

    def create(self, validated_data):
        periodo = validated_data.pop('valido_desde')
        parametros = ParametrosGenerales(**validated_data)
        parametros.valido_desde_id = periodo["pk"]
        parametros.save()
        return parametros

    def update(self, instance, validated_data):
        valido_desde = validated_data.pop('valido_desde')
        for attr in validated_data.keys():
            setattr(instance, attr, validated_data.get(attr, getattr(instance, attr)))
        instance.valido_desde_id = valido_desde.get('pk', instance.valido_desde_id)
        instance.save()
        return instance


class RegistroAsistenciaEquipoSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)
    equipo = EquipoSerializer(read_only=True)
    equipo_id = serializers.IntegerField(source='equipo.pk')
    centro_costo = ObrasSerializer(read_only=True)
    centro_costo_id = serializers.IntegerField(source='centro_costo.pk')
    asistencia_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = RegistroAsistenciaEquipo
        fields = ('pk', 'asistencia_id', 'equipo', 'equipo_id', 'centro_costo', 'centro_costo_id', )

    def create(self, validated_data):
        # el alta es desde el serializer general
        raise exceptions.PermissionDenied

    def update(self, instance, validated_data):
        equipo = validated_data.pop('equipo')
        centro_costo = validated_data.pop('centro_costo')
        for attr in validated_data.keys():
            setattr(instance, attr, validated_data.get(attr, getattr(instance, attr)))
        instance.equipo_id = equipo.get('pk', instance.equipo_id)
        instance.centro_costo_id = centro_costo.get('pk', instance.centro_costo_id)
        instance.save()
        return instance


class AsistenciaEquipoSerializer(serializers.ModelSerializer):
    registros = RegistroAsistenciaEquipoSerializer(many=True)

    class Meta:
        model = AsistenciaEquipo
        fields = ('pk', 'dia', 'registros')

    @atomic
    def create(self, validated_data):
        registros = validated_data.pop('registros')
        asistencia = AsistenciaEquipo(**validated_data)
        try:
            asistencia.save()
        except IntegrityError:
            raise serializers.ValidationError('%s existente' % self.Meta.model._meta.verbose_name)
        for item_data in registros:
            registro = RegistroAsistenciaEquipo()
            registro.asistencia = asistencia
            registro.equipo_id = item_data.get('equipo').get('pk')
            registro.centro_costo_id = item_data.get('centro_costo').get('pk')
            registro.save()
        return asistencia

    @atomic
    def update(self, instance, validated_data):
        registros = validated_data.pop('registros')
        instance.dia = validated_data.get('dia', instance.dia)
        instance.save()

        exists_pks = []
        for item in registros:
            if "pk" in item:
                pk = item.pop('pk')
                exists_pks.append(pk)
                item_obj, _ = RegistroAsistenciaEquipo.objects.update_or_create(
                    pk=pk, asistencia=instance, defaults={
                        'equipo_id': item.get('equipo').get('pk'),
                        'centro_costo_id': item.get('centro_costo').get('pk')
                    })
            else:
                item_obj = RegistroAsistenciaEquipo()
                item_obj.asistencia = instance
                item_obj.equipo_id = item.get('equipo').get('pk')
                item_obj.centro_costo_id = item.get('centro_costo').get('pk')
                item_obj.save()
                exists_pks.append(item_obj.pk)
        # eliminar items no enviados
        instance.registros.exclude(pk__in=exists_pks).delete()
        return instance


class ReportAsistenciaItemCCSerializer(serializers.Serializer):
    equipo = EquipoSerializer(read_only=True)
    equipo_id = serializers.IntegerField()
    centro_costo = ObrasSerializer(read_only=True)
    centro_costo_id = serializers.IntegerField()
    dias = serializers.IntegerField()
    horas = serializers.IntegerField()
    costo_hs = serializers.DecimalField(max_digits=18, decimal_places=2, default=0)
    costo_diario = serializers.DecimalField(max_digits=18, decimal_places=2, default=0)
    costo_total = serializers.SerializerMethodField()

    def get_costo_total(self, obj):
        return "%.2f" % (obj["costo_diario"] * obj["dias"])


class CostoEquipoValoresTallerSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)
    equipo = EquipoSerializer(read_only=True)
    equipo_id = serializers.IntegerField(source='equipo.pk')
    valido_desde = PeriodoSerializer(read_only=True)
    valido_desde_id = serializers.IntegerField(source='valido_desde.pk', read_only=True)
    costo_mensual_mo_logistico = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = CostoEquipoValores
        fields = (
            'pk', 'equipo', 'equipo_id', 'valido_desde', 'valido_desde_id', 'markup',
            'costo_mensual_del_activo_calculado',
            'costo_mensual_del_activo_con_mo_calculado',
            'costo_equipo_calculado',
            'costo_mensual_mo_logistico'
        )
        read_only_fields = (
            'pk', 'equipo', 'equipo_id', 'valido_desde', 'valido_desde_id',
            'costo_mensual_del_activo_calculado',
            'costo_mensual_del_activo_con_mo_calculado',
            'costo_equipo_calculado',
            'costo_mensual_mo_logistico'
        )


class TableroControlTallerSerializer(CostoEquipoValoresTallerSerializer):
    periodo_id = serializers.IntegerField(source='valido_desde.pk')
    costo_mensual_lubricante = serializers.SerializerMethodField()
    costo_mensual_tren_rodaje = serializers.SerializerMethodField()
    costo_mensual_posesion = serializers.SerializerMethodField()
    costo_mensual_reparacion = serializers.SerializerMethodField()

    class Meta:
        model = CostoEquipoValores
        fields = (
            'equipo', 'equipo_id', 'periodo_id', 'markup',
            'costo_mensual_del_activo_calculado',
            'costo_mensual_del_activo_con_mo_calculado',
            'costo_equipo_calculado',
            'costo_mensual_lubricante',
            'costo_mensual_tren_rodaje',
            'costo_mensual_posesion',
            'costo_mensual_reparacion',
            'costo_mensual_mo_logistico'
        )

    # def get_costo_mensual_del_activo(self, obj):
    #     if obj.equipo.es_alquilado:
    #         return 0
    #     return "%.2f" % obj.costo_mensual_del_activo

    # def get_costo_mensual_del_activo_con_mo(self, obj):
    #     if obj.equipo.es_alquilado:
    #         return 0
    #     return "%.2f" % obj.costo_mensual_del_activo_con_mo

    # def get_costo_mensual(self, obj):
    #     return "%.2f" % obj.costo_mensual_zille

    def get_costo_mensual_lubricante(self, obj):
        try:
            val = LubricantesValores.objects.vigente(obj.equipo, obj.valido_desde)
            return "%.2f" % val.costo_total_pesos_mes
        except (ObjectDoesNotExist, AttributeError):
            return 0

    def get_costo_mensual_tren_rodaje(self, obj):
        try:
            val = TrenRodajeValores.objects.vigente(obj.equipo, obj.valido_desde)
            return "%.2f" % val.costo_total_pesos_mes
        except (ObjectDoesNotExist, AttributeError):
            return 0

    def get_costo_mensual_posesion(self, obj):
        try:
            val = PosesionValores.objects.vigente(obj.equipo, obj.valido_desde)
            return "%.2f" % val.costo_total_pesos_mes
        except (ObjectDoesNotExist, AttributeError):
            return 0

    def get_costo_mensual_reparacion(self, obj):
        try:
            val = ReparacionesValores.objects.vigente(obj.equipo, obj.valido_desde)
            return "%.2f" % val.costo_total_pesos_mes
        except (ObjectDoesNotExist, AttributeError):
            return 0


class LubricanteItemSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)
    class Meta:
        model = LubricanteItem
        fields = ('pk', 'descripcion', 'es_filtro', 'observaciones')


class ValoresByItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    nuevo_valor = serializers.DecimalField(max_digits=18, decimal_places=2)


class LubricantesParametrosItemSerializer(serializers.ModelSerializer):
    item = LubricanteItemSerializer()

    class Meta:
        model = LubricantesParametrosItem
        fields = ('item', 'cambios_por_anio', 'volumen_por_cambio')


class LubricantesParametrosItemThinSerializer(serializers.ModelSerializer):

    class Meta:
        model = LubricantesParametrosItem
        fields = ('cambios_por_anio', 'volumen_por_cambio')


class LubricantesParametrosSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)
    items = LubricantesParametrosItemSerializer(many=True, source='items_lubricante')
    class Meta:
        model = LubricantesParametros
        fields = ('pk', 'valido_desde', 'equipo', 'hp', 'items')


class LubricantesValoresItemSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)
    item = LubricanteItemSerializer()
    parametros = LubricantesParametrosItemThinSerializer(source='parametro_item', read_only=True)

    class Meta:
        model = LubricantesValoresItem
        fields = ('pk', 'item', 'parametros', 'valor_unitario', 'costo_por_mes')


class ValoresLubricantesTallerSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)
    valido_desde = PeriodoSerializer(read_only=True)
    valido_desde_id = serializers.IntegerField(source='valido_desde.pk')
    equipo = EquipoSerializer(read_only=True)
    equipo_id = serializers.IntegerField(source='equipo.pk')
    parametros_pk = serializers.IntegerField(source='mis_parametros.pk', read_only=True)

    items = LubricantesValoresItemSerializer(many=True, source='valores')

    class Meta:
        model = LubricantesValores
        fields = ('pk', 'valido_desde', 'valido_desde_id', 'equipo', 'equipo_id', 'parametros_pk',
                  'items', 'costo_total_pesos_hora', 'costo_total_pesos_mes')

    @atomic
    def create(self, validated_data):
        items = validated_data.pop('valores')
        valor = LubricantesValores(**validated_data)
        try:
            valor.save()
        except IntegrityError:
            raise serializers.ValidationError('%s existente' % self.Meta.model._meta.verbose_name)
        for item_data in items:
            registro = LubricantesValoresItem()
            registro.item_id = item_data.get('item').get('pk')
            registro.valor_unitario = item_data.get('valor_unitario')
            registro.valor = valor
            registro.save()
        return valor

    @atomic
    def update(self, instance, validated_data):
        items = validated_data.pop('valores')
        instance.equipo_id = validated_data.get('equipo', instance.equipo_id).get('pk', instance.equipo_id)
        instance.valido_desde_id = validated_data.get('valido_desde', instance.valido_desde_id).get('pk', instance.valido_desde_id)
        instance.save()

        exists_pks = []
        for item_data in items:
            item_id = item_data.get('item').get('pk')
            val_item, created = LubricantesValoresItem.objects.update_or_create(
                valor=instance,
                item_id=item_id,
                defaults={
                    'valor_unitario': item_data.get('valor_unitario')
                }
            )
            exists_pks.append(val_item.pk)

        # eliminar items no enviados
        instance.valores.exclude(pk__in=exists_pks).delete()
        return instance


class TrenRodajeParametrosSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = TrenRodajeParametros
        fields = (
            'pk', 'vida_util_neumatico', 'cantidad_neumaticos', 'medidas',
            'factor_basico', 'impacto', 'abracion', 'z', 'tiene_neumaticos'
        )


class ValoresTrenRodajeTallerSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)
    valido_desde = PeriodoSerializer(read_only=True)
    valido_desde_id = serializers.IntegerField(source='valido_desde.pk', read_only=True)
    equipo = EquipoSerializer(read_only=True)
    equipo_id = serializers.IntegerField()

    parametros = TrenRodajeParametrosSerializer(source='mis_parametros', read_only=True)

    class Meta:
        model = TrenRodajeValores
        fields = ('pk', 'valido_desde', 'valido_desde_id', 'equipo', 'equipo_id',
                  'precio_neumatico', 'parametros', 'costo_total_pesos_hora',
                  'costo_total_pesos_mes')


class PosesionParametrosSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = PosesionParametros
        fields = (
            'pk', 'posesion_hs', 'precio_del_activo', 'residual',
            'residual_en_USD', 'posesion_en_anios',
        )


class ValoresPosesionTallerSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)
    valido_desde = PeriodoSerializer(read_only=True)
    valido_desde_id = serializers.IntegerField(source='valido_desde.pk', read_only=True)
    equipo = EquipoSerializer(read_only=True)
    equipo_id = serializers.IntegerField()

    parametros = PosesionParametrosSerializer(source='mis_parametros', read_only=True)

    class Meta:
        model = PosesionValores
        fields = (
            'pk', 'valido_desde', 'valido_desde_id', 'equipo', 'equipo_id',
            'seguros', 'ruta', 'vtv', 'certificacion', 'habilitaciones', 'rsv', 'vhf', 'impuestos',
            'parametros', 'costo_total_pesos_hora', 'costo_total_pesos_mes'
        )


class ReparacionesParametrosSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = ReparacionesParametros
        fields = (
            'pk', 'factor_basico', 'multiplicador',
        )


class ValoresReparacionesTallerSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)
    valido_desde = PeriodoSerializer(read_only=True)
    valido_desde_id = serializers.IntegerField(source='valido_desde.pk', read_only=True)
    equipo = EquipoSerializer(read_only=True)
    equipo_id = serializers.IntegerField(source='equipo.pk', read_only=True)

    parametros = ReparacionesParametrosSerializer(source='mis_parametros', read_only=True)

    class Meta:
        model = ReparacionesValores
        fields = (
            'pk', 'valido_desde', 'valido_desde_id', 'equipo', 'equipo_id',
            'parametros', 'costo_total_pesos_hora', 'costo_total_pesos_mes'
        )


class ValoresManoObraTallerSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)
    valido_desde = PeriodoSerializer(read_only=True)
    valido_desde_id = serializers.IntegerField(source='valido_desde.pk')

    class Meta:
        model = ManoObraValores
        fields = (
            'pk', 'valido_desde', 'valido_desde_id',
            'taller', 'plataforma_combustible',
            'carretones'
        )

    @atomic
    def create(self, validated_data):
        valido_desde = validated_data.pop('valido_desde')
        valores = ManoObraValores(**validated_data)
        valores.valido_desde_id = valido_desde["pk"]
        try:
            valores.save()
        except IntegrityError:
            raise serializers.ValidationError('Ya existe valores de mano de obra para el periodo')
        return valores

    @atomic
    def update(self, instance, validated_data):
        instance.valido_desde_id = validated_data.get('valido_desde', instance.valido_desde_id).get('pk', instance.valido_desde_id)
        instance.taller = validated_data.get('taller', instance.taller)
        instance.plataforma_combustible = validated_data.get('plataforma_combustible', instance.plataforma_combustible)
        instance.carretones = validated_data.get('carretones', instance.carretones)
        try:
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError('Ya existe valores de mano de obra para el periodo.')
        return instance


class ValoresEquipoAlquiladoTallerSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=False)
    valido_desde = PeriodoSerializer(read_only=True)
    valido_desde_id = serializers.IntegerField(source='valido_desde.pk', read_only=True)
    equipo = EquipoSerializer(read_only=True)
    equipo_id = serializers.IntegerField()

    class Meta:
        model = EquipoAlquiladoValores
        fields = (
            'pk', 'valido_desde', 'valido_desde_id', 'equipo', 'equipo_id',
            'alquiler', 'comentarios',
        )
