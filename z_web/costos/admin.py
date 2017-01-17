from django.contrib import admin

from .models import (CostoManoObra, CostoSubContrato, LubricanteFluidosHidro,
                     TrenRodaje, ReserveReparaciones, MaterialesTotal,
                     CostoParametro, CostoPosesion, ArchivosAdjuntosPeriodo)
from zweb_utils.format import currency_format as cur


@admin.register(CostoParametro)
class CostoParametroAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'horas_dia', 'dias_mes', 'horas_año', 'pesos_usd', 'precio_go')
    # readonly_fields = ('fecha_alta', 'fecha_baja', )

    # def save_model(self, request, obj, form, change):
    #     # al modificar, creo uno nuevo y establezco la fecha fin del anterior
    #     if change:
    #         id = obj.pk
    #         obj.pk = None
    #         CostoParametro.objects.filter(pk=id).update(fecha_baja=datetime.now())
    #     else:
    #         CostoParametro.objects.filter(fecha_baja=None).update(fecha_baja=datetime.now())
    #     obj.save()


@admin.register(CostoManoObra)
class CostoManoObraAdmin(admin.ModelAdmin):
    list_display = ('obra', 'periodo', 'monto_format',)
    list_filter = ('obra', 'periodo', )

    def monto_format(self, obj):
        return cur(obj.monto)
    monto_format.short_description = "Costo ($)"


@admin.register(CostoSubContrato)
class CostoSubContratoAdmin(admin.ModelAdmin):
    list_display = ('obra', 'periodo', 'monto_format', 'descripcion', )
    list_filter = ('obra', 'periodo', )
    ordering = ('-periodo__fecha_inicio', )

    def monto_format(self, obj):
        return cur(obj.monto)
    monto_format.short_description = "Costo ($)"

@admin.register(MaterialesTotal)
class MaterialesTotalAdmin(admin.ModelAdmin):
    list_display = ('obra', 'periodo', 'monto_format', )
    list_filter = ('obra', 'periodo', )
    ordering = ('-periodo__fecha_inicio', )

    def monto_format(self, obj):
        return cur(obj.monto)
    monto_format.short_description = "Costo ($)"


class AbstractAdmin(admin.ModelAdmin):
    list_display = ('familia_equipo', 'periodo', 'monto_hora_format', 'monto_mes_format', )
    list_filter = ('familia_equipo', 'periodo', )
    ordering = ('-periodo__fecha_inicio', )

    def monto_hora_format(self, obj):
        return cur(obj.monto_hora)
    monto_hora_format.short_description = "Costo ($/hs)"

    def monto_mes_format(self, obj):
        return cur(obj.monto_mes)
    monto_mes_format.short_description = "Costo ($/mes)"


@admin.register(LubricanteFluidosHidro)
class LubricanteFluidosHidroAdmin(AbstractAdmin):
    pass


@admin.register(TrenRodaje)
class TrenRodajeAdmin(AbstractAdmin):
    pass


@admin.register(ReserveReparaciones)
class ReserveReparacionesAdmin(AbstractAdmin):

    pass


@admin.register(CostoPosesion)
class CostoPosesionAdmin(AbstractAdmin):
    pass


@admin.register(ArchivosAdjuntosPeriodo)
class ArchivosAdjuntosPeriodoAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'archivo', 'comentario')
