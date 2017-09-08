from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from core.models import (Equipos, EstServicio, FrancoLicencia, Obras,
                         Operarios, Usuario, CCT, UserExtension)


@admin.register(Equipos)
class Equipos(admin.ModelAdmin):
    list_display = ('n_interno', 'familia_equipo', 'equipo', 'marca', 'modelo', 'año', 'dominio', )
    list_filter = ('marca', 'año', 'familia_equipo', )
    search_fields = ('n_interno', 'equipo', 'año', 'dominio', 'modelo')
    ordering = ('n_interno', )
    list_display_links = ('n_interno', 'equipo', )
    fieldsets = (
        (None, {
            'fields': (('familia_equipo', 'equipo'),
                       ('n_interno', 'nro_serie'),
                       ('marca', 'modelo',),
                       ('dominio',  'año'), )
        }),
        ("Vencimientos", {
            'fields': (('vto_vtv', 'vto_seguro', 'vto_ruta'),
                       ('vto_certificacion', 'vto_certificacion_obs'),
                       ('descripcion_vto1', 'vto_otros1', ),
                       ('descripcion_vto2', 'vto_otros2', ),
                       ('descripcion_vto3', 'vto_otros3', ))
        })
    )


@admin.register(EstServicio)
class EstacionServicioAdmin(admin.ModelAdmin):
    pass


@admin.register(Obras)
class ObrasAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'obra', 'cuit', 'lugar', 'responsable', 'is_active', 'es_cc', 'prorratea_costos')
    list_filter = ('responsable', 'descuenta_francos', 'descuenta_licencias', "es_cc", 'prorratea_costos')
    search_fields = ('codigo', 'obra', 'comitente', 'responsable', 'cuit', )
    ordering = ('fecha_fin', 'codigo', '-es_cc',)
    fieldsets = (
        (None, {
            'fields': (('codigo', 'obra', 'fecha_inicio', 'fecha_fin'),
                       ('cuit', 'lugar', 'plazo'),
                       ('contrato', 'comitente', 'responsable',))
        }),
        ("Configuración General", {
            'fields': ('tiene_registro', 'tiene_equipo', 'descuenta_francos', 'descuenta_licencias', )
        }),
        ("Configuración de registro horario", {
            'fields': ('tiene_comida', 'tiene_vianda', 'tiene_desarraigo', 'limite_vianda_doble', )
        }),
        ("Configuración de costos", {
            'fields': ('es_cc', 'prorratea_costos', )
        })
    )
    def is_active(self, obj):
        return obj.esta_activa
    is_active.short_description = "¿Activa?"
    is_active.boolean = True


class FrancoLicenciaInlineAdmin(admin.StackedInline):
    extra = 0
    can_delete = False
    model = FrancoLicencia
    max_num = 1
    fieldsets = (
        ("Parámetros de ajustes", {
            'fields': (('ajuste_francos', 'ajuste_licencias', 'pagados',),)
        }),
        ("Solicitud de días", {
            'fields': (('solicitados1', 'sale1', 'entra1', ),
                       ('solicitados2', 'sale2', 'entra2', )),
        }),
    )


@admin.register(CCT)
class CCTAdmin(admin.ModelAdmin):
    pass


@admin.register(Operarios)
class OperariosAdmin(admin.ModelAdmin):
    list_display = ('n_legajo', 'nombre', 'cuil', 'funcion', 'cct', 'desarraigo',
                    'fecha_ingreso', 'observaciones')
    list_filter = ('funcion', 'desarraigo', 'cct')
    search_fields = ('^n_legajo', '^cuil', 'nombre', '^fecha_ingreso', )
    list_display_links = ('n_legajo', 'nombre', )
    fieldsets = (
        (None, {
            'fields': (('n_legajo', 'cuil', ),
                       ('nombre', ))
        }),

        ('Funciones', {
            'fields': (('cct', 'funcion', 'desarraigo',), )
        }),
        ('Fechas Importantes', {
            'fields': ('fecha_ingreso',
                       ('vto_carnet', 'vto_psicofisico'),
                       ('vto_cargagral', 'vto_cargapeligrosa'), )
        }),
        ('Vencimientos extras', {
            'classes': ('collapse',),
            'fields': (('descripcion_vto1', 'vto_otros1', ),
                       ('descripcion_vto2', 'vto_otros2', ),
                       ('descripcion_vto3', 'vto_otros3', ),)
        }),
        ("Observaciones", {
            'classes': ('collapse',),
            'fields': ('observaciones', )
        }),
    )
    inlines = [FrancoLicenciaInlineAdmin, ]


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rol', 'is_active')
    list_filter = ('rol',)
    search_fields = ('user', 'rol', )
    list_display_links = ('user',)
    fields = ('user', 'rol', 'fechabaja', )

    def is_active(self, obj):
        return obj.fechabaja is None
    is_active.short_description = "Usuario activo"
    is_active.boolean = True


class UserExtensionInline(admin.StackedInline):
    model = UserExtension
    max_num = 1
    min_num = 0


class CustomUserAdmin(UserAdmin):
    inlines = UserAdmin.inlines + [UserExtensionInline]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
