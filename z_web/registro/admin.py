from datetime import datetime
from django.contrib import admin
from django import forms

from core.models import Obras
from .models import (Alarma, Combustible, Partediario, Registro, Materiales,
                     RegistroEquipo, PrecioHistorico, Certificacion, AjusteCombustible,
                     CertificacionInterna)
from zweb_utils.format import currency_format as cur


@admin.register(Alarma)
class AlarmaAdmin(admin.ModelAdmin):
    model = Alarma
    list_display = ['alert_status', 'fecha', 'nombre', 'comentario', ]
    order_by = ['-fecha', ]

    def alert_status(self, obj):
        now = datetime.now().date()
        diff = (obj.fecha - now).days
        if diff >= 20:
            return '<i class="icon-time label-success"></i> En %s días' % diff
        elif diff < 20 and diff >= 0:
            return '<i class="icon-time label-warning"></i> En %s' % diff
        else:
            return '<i class="icon-time label-danger"></i> Pasada en %s días' % (diff*-1)
    alert_status.short_description = "Estado"
    alert_status.allow_tags = True


class RegistroAdminInline(admin.StackedInline):
    model = Registro
    extra = 0
    max_num = 1
    can_delete = False
    fieldsets = (
        (None, {
            'fields': (('fecha', 'dia', 'especial'), )
        }),
        ("Horarios", {
            'fields': (('hs_salida', 'hs_inicio',),
                       ('hs_ialmuerzo', 'hs_falmuerzo',),
                       ('hs_fin', 'hs_llegada', ))
        }),
        ("Hs resultantes - Calculados", {
            'fields': (('hs_normal', 'hs_viaje', 'hs_almuerzo', 'hs_50', ),
                       ('hs_100', 'hs_total', 'hs_tarea', ))
        }),
    )
    readonly_fields = ('hs_normal', 'hs_viaje', 'hs_almuerzo', 'hs_50', 'hs_100', 'hs_total', 'hs_tarea', )


class RegistroEquipoAdminInline(admin.StackedInline):
    model = RegistroEquipo
    extra = 0
    max_num = 1
    can_delete = False
    fieldsets = (
        (None, {
            'fields': (('equipo', ),
                       ('ini_horo', 'fin_horo'),
                       ('ini_odo', 'fin_odo'),
                       ('tarea', ),
                       )
        }),
        ("Combustible", {
            'fields': (('estacion_servicio', 'est_servicio',),
                        ('cant_combustible', ))
        }),
    )


class MaterialesAdminInline(admin.StackedInline):
    model = Materiales
    extra = 0
    fieldsets = (
        ("Materiales transportados", {
            'fields': (("material", 'cantidad',),
                       ('distancia', 'viajes',),
                       'cantera_cargadero',)
        }),
    )


@admin.register(Partediario)
class PartediarioAdmin(admin.ModelAdmin):
    model = Partediario
    list_display = ('fecha', 'numero', 'operario', 'obra', 'multifuncion', 'desarraigo',)
    order_by = ('-fecha', )
    list_select_related = ('operario', 'obra', 'registro_equipo', )
    search_fields = ['numero', '^operario__nombre', 'fecha']
    list_filter = ('obra', 'multifuncion', 'desarraigo', )
    inlines = [RegistroEquipoAdminInline, RegistroAdminInline, MaterialesAdminInline, ]


# @admin.register(Combustible)
# class CombustibleAdmin(admin.ModelAdmin):
#     pass


# @admin.register(PrecioHistorico)
# class PrecioHistoricoAdmin(admin.ModelAdmin):
#     list_display = ('familia', 'tipo', 'valor_format', 'fechaalta', 'fechabaja')
#     list_filter = ('familia', 'tipo', )
#
#     def valor_format(self, obj):
#         return cur(obj.valor)
#     valor_format.short_description = "Valor ($)"


class CertificacionAdminForm(forms.ModelForm):
    obra = forms.ModelChoiceField(queryset=Obras.objects.filter(
        es_cc=True, fecha_fin__isnull=True).order_by('fecha_inicio'))

    class Meta:
        model = Certificacion
        fields = ('periodo', 'obra', 'monto', )


@admin.register(Certificacion)
class CertificacionAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'obra', 'valor_format')
    list_filter = ('periodo', 'obra', )
    form = CertificacionAdminForm

    def valor_format(self, obj):
        return cur(obj.monto)
    valor_format.short_description = "Monto ($)"


class AjusteCombustibleAdminForm(forms.ModelForm):
    obra = forms.ModelChoiceField(queryset=Obras.objects.filter(
        es_cc=True, fecha_fin__isnull=True).order_by('fecha_inicio'))

    class Meta:
        model = AjusteCombustible
        fields = ('periodo', 'obra', 'valor', 'costo_total', 'comentarios')


@admin.register(AjusteCombustible)
class AjusteCombustibleAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'obra', 'valor_format', 'total_format', 'comentarios')
    list_filter = ('periodo', 'obra', )
    form = AjusteCombustibleAdminForm

    def valor_format(self, obj):
        return cur(obj.valor) if obj.valor else ''
    valor_format.short_description = "Valor del ajuste ($)"

    def total_format(self, obj):
        return cur(obj.costo_total) if obj.costo_total else ''
    total_format.short_description = "Costo total ($)"


class CertificacionInternaAdminForm(forms.ModelForm):
    obra = forms.ModelChoiceField(queryset=Obras.objects.filter(
        es_cc=True, fecha_fin__isnull=True).order_by('fecha_inicio'))

    class Meta:
        model = CertificacionInterna
        fields = ('periodo', 'obra', 'monto', )


@admin.register(CertificacionInterna)
class CertificacionInternaAdmin(admin.ModelAdmin):
    list_display = ('obra', 'periodo', 'monto_format', )
    list_filter = ('obra', 'periodo', )
    ordering = ('-periodo__fecha_inicio', )
    form = CertificacionInternaAdminForm

    def monto_format(self, obj):
        return cur(obj.monto)
    monto_format.short_description = "Costo ($)"
