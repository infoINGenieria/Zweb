from django.contrib import admin

from model_utils.managers import QueryManager

from .models import CostoParametro, ArchivosAdjuntosPeriodo, CostoReal, CostoTipo, CostoProyeccion
from .forms import CostoEditPorCCForm, CostoEditPorEquipoForm


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


@admin.register(ArchivosAdjuntosPeriodo)
class ArchivosAdjuntosPeriodoAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'archivo', 'comentario')


@admin.register(CostoTipo)
class CostoTipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'relacionado_con', 'unidad_monto')
    list_filter = ('relacionado_con', 'unidad_monto', )


@admin.register(CostoReal)
class CostoAdmin(admin.ModelAdmin):
    list_display = ('tipo_costo', 'periodo', 'centro_costo', 'familia_equipo')
    list_filter = ('periodo', 'tipo_costo', 'centro_costo', 'familia_equipo', )

    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            return super(CostoAdmin, self).get_form(request, obj, **kwargs)
        if obj.tipo_costo.es_por_cc:
            return CostoEditPorCCForm
        else:
            return CostoEditPorEquipoForm

    def has_add_permission(self, request):
        return False


@admin.register(CostoProyeccion)
class CostoProyeccionAdmin(CostoAdmin):

    def has_add_permission(self, request):
        return True


# # Registramos todos los proxies de los costos
# def create_proxy_admin(model_admin, model, name, tipo_costo):

#     # el crear el proxy para el admin
#     class  Meta:
#         proxy = True
#         app_label = model._meta.app_label
#         verbose_name = verbose_name_plural = tipo_costo.nombre

#     attrs = {
#         '__module__': '',
#         'Meta': Meta,
#         'objects': QueryManager(tipo_costo=tipo_costo).order_by("-periodo")
#         }
#     proxy_model = type(name, (model, ), attrs)

#     # registrar el proxy en el admin
#     admin.site.register(proxy_model, model_admin)

# for tipo_costo in CostoTipo.objects.all():
#     # nombre de la clase
#     name = "{}".format(tipo_costo.nombre.capitalize().replace(" ", ""))

#     admin_attrs = {
#         'list_display': ('periodo', 'centro_costo', 'familia_equipo'),
#     }

#     # Create ModelAdmin class
#     Admin = type("{}Admin".format(name), (admin.ModelAdmin, ), admin_attrs)

#     # Create proxy model and register with admin
#     create_proxy_admin(Admin, Costo, name, tipo_costo)
