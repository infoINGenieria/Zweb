from django.contrib import admin

from .models import (
    ParametrosGenerales,
    LubricantesParametros, LubricantesValores,
    TrenRodajeParametros, TrenRodajeValores,
    PosesionParametros, PosesionValores,
    ReparacionesParametros, ReparacionesValores,
    ManoObraValores, EquipoAlquiladoValores,
    CostoEquipoValores, LubricanteItem,
    LubricantesParametrosItem, LubricantesValoresItem)


class LubricantesParametrosItemInline(admin.StackedInline):
    model = LubricantesParametrosItem
    can_delete = True


class LubricantesValoresItemInline(admin.StackedInline):
    model = LubricantesValoresItem
    can_delete = True


@admin.register(ParametrosGenerales)
class ParametrosGeneralesAdmin(admin.ModelAdmin):
    list_display = ('valido_desde', 'valor_dolar', )
    search_fields = ('valido_desde', )

    def get_changeform_initial_data(self, request):
        last = ParametrosGenerales.objects.latest('valido_desde__fecha_fin')
        return last.__dict__


@admin.register(LubricanteItem)
class LubricanteItemAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'observaciones', 'tipo')

    def tipo(self, obj):
        return "Filtro" if obj.es_filtro else "Lubricante /F. Hidráulico"
    tipo.short_description = "Tipo"


@admin.register(LubricantesParametros)
class LubricantesParametrosAdmin(admin.ModelAdmin):
    search_fields = ['equipo__n_interno']
    inlines = [LubricantesParametrosItemInline]
    list_display = ('equipo', 'valido_desde', 'hp', 'cantidad_lubri', 'cantidad_filtros')

    def cantidad_lubri(self, obj):
        return obj.items_lubricante.filter(item__es_filtro=False).count()
    cantidad_lubri.short_description = "Cantidad items Lubri / Hidra"

    def cantidad_filtros(self, obj):
        return obj.items_lubricante.filter(item__es_filtro=True).count()
    cantidad_filtros.short_description = "Cantidad items filtros"


@admin.register(LubricantesValores)
class LubricantesValoresAdmin(admin.ModelAdmin):
    search_fields = ['equipo__n_interno']
    inlines = [LubricantesValoresItemInline]
    list_display = ('equipo', 'valido_desde', 'costo_total_pesos_mes')


@admin.register(TrenRodajeParametros)
class TrenRodajeParametrosAdmin(admin.ModelAdmin):
    search_fields = ['equipo__n_interno']
    list_display = ('equipo', 'valido_desde')


@admin.register(TrenRodajeValores)
class TrenRodajeValoresAdmin(admin.ModelAdmin):
    search_fields = ['equipo__n_interno']
    list_display = ('equipo', 'valido_desde', 'costo_total_pesos_mes')


@admin.register(PosesionParametros)
class PosesionParametrosAdmin(admin.ModelAdmin):
    search_fields = ['equipo__n_interno']
    list_display = ('equipo', 'valido_desde')


@admin.register(PosesionValores)
class PosesionValoresAdmin(admin.ModelAdmin):
    search_fields = ['equipo__n_interno']
    list_display = ('equipo', 'valido_desde', 'costo_total_pesos_mes')


@admin.register(ReparacionesParametros)
class ReparacionesParametrosAdmin(admin.ModelAdmin):
    search_fields = ['equipo__n_interno']
    list_display = ('equipo', 'valido_desde')


@admin.register(ReparacionesValores)
class ReparacionesValoresAdmin(admin.ModelAdmin):
    search_fields = ['equipo__n_interno']
    list_display = ('equipo', 'valido_desde', 'costo_total_pesos_mes')


@admin.register(ManoObraValores)
class ManoObraValoresAdmin(admin.ModelAdmin):
    search_fields = ['valido_desde']
    list_display = ('valido_desde', )


@admin.register(EquipoAlquiladoValores)
class EquipoAlquiladoValoresAdmin(admin.ModelAdmin):
    search_fields = ['equipo__n_interno']
    list_display = ('equipo', 'valido_desde',)


@admin.register(CostoEquipoValores)
class CostoEquipoValoresAdmin(admin.ModelAdmin):
    search_fields = ['equipo__n_interno']
    list_display = ('equipo', 'valido_desde', )
