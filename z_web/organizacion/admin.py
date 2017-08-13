from django.contrib import admin

from organizacion.models import UnidadNegocio


@admin.register(UnidadNegocio)
class UnidadNegocioAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre', )
    list_display_links = ('codigo',)

