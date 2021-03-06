from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from core.models import (
    Equipos, EstServicio, FrancoLicencia, Obras,
    Operarios, Usuario, CCT, UserExtension, InfoObra)
from core.actions import set_baja_equipo, set_baja_obra


@admin.register(Equipos)
class Equipos(admin.ModelAdmin):
    list_display = ('n_interno', 'familia_equipo', 'equipo', 'marca', 'modelo', 'año', 'dominio', 'es_alquilado', 'fecha_baja')
    list_filter = ('marca', 'año', 'familia_equipo', 'es_alquilado', )
    search_fields = ('n_interno', 'equipo', 'año', 'dominio', 'modelo')
    ordering = ('n_interno', )
    list_display_links = ('n_interno', 'equipo', )
    actions = [set_baja_equipo]
    fieldsets = (
        (None, {
            'fields': (('familia_equipo', 'equipo'),
                       ('n_interno', 'nro_serie'),
                       ('marca', 'modelo',),
                       ('dominio',  'año'),
                       ('es_alquilado',  'fecha_baja'),
                       ('excluir_costos_taller', ),
                       ('implica_mo_logistica', ),
                       )
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

class InfoObraInline(admin.StackedInline):
    model = InfoObra
    can_delete = False
    max_num = 1


@admin.register(Obras)
class ObrasAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'obra', 'deposito', 'cuit', 'lugar', 'responsable', 'is_active', 'es_cc', 'prorratea_costos')
    list_filter = ('responsable', 'descuenta_francos', 'descuenta_licencias', "es_cc", 'prorratea_costos')
    search_fields = ('codigo', 'obra', 'comitente', 'responsable', 'cuit', 'deposito')
    ordering = ('fecha_fin', 'codigo', '-es_cc',)
    inlines = [InfoObraInline, ]
    actions = [set_baja_obra]
    fieldsets = (
        (None, {
            'fields': (('codigo', 'obra', 'deposito', 'fecha_inicio', 'fecha_fin'),
                       ('cuit', 'lugar', 'plazo', 'unidad_negocio'),
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

    def get_queryset(self, request, **kwargs):
        qs = Obras.get_obras_by_un(request.user)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        unidades_negocio = request.user.extension.unidades_negocio.all()
        if unidades_negocio.count() == 1:
            # si tiene, ocultamos el campo
            self.fieldsets[0][1]["fields"] = (
                ('codigo', 'obra', 'deposito', 'fecha_inicio', 'fecha_fin'),
                ('cuit', 'lugar', 'plazo'),
                ('contrato', 'comitente', 'responsable',)
            )
        form = super(ObrasAdmin, self).get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        unidades_negocio = request.user.extension.unidades_negocio.all()
        if unidades_negocio.count() == 1:
            unidad_negocio = unidades_negocio.get()
            if not obj.unidad_negocio or (
                    obj.unidad_negocio and obj.unidad_negocio_id != unidad_negocio.pk):
                obj.unidad_negocio = unidad_negocio
        super(ObrasAdmin, self).save_model(request, obj, form, change)


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
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'un')
    inlines = UserAdmin.inlines + [UserExtensionInline]

    def un(self, obj):
        try:
            return obj.extension.unidad_negocio.codigo
        except:
            return "-"
    un.short_description = "Unidad de negocio"

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
