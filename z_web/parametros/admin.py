from django.contrib import admin

from .models import Situacion, Parametro, Funcion, FamiliaEquipo, TipoCosto, Periodo


# @admin.register(Situacion)
# class SituacionAdmin(admin.ModelAdmin):
#     pass


@admin.register(Parametro)
class ParametroAdmin(admin.ModelAdmin):
    pass


@admin.register(Funcion)
class FuncionAdmin(admin.ModelAdmin):
    pass


@admin.register(FamiliaEquipo)
class FamiliaEquipoAdmin(admin.ModelAdmin):
    pass


# @admin.register(TipoCosto)
# class TipoCostoAdmin(admin.ModelAdmin):
#     pass


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'fecha_inicio', 'fecha_fin', )
    ordering = ('-fecha_inicio', )

    def get_form(self, *args, **kwargs):
        """
        Hacemos readonly los datepicker.ArithmeticError
        """
        f = super(PeriodoAdmin, self).get_form(*args, **kwargs)
        f.base_fields["fecha_inicio"].widget.attrs.update({"readonly": "readonly"})
        f.base_fields["fecha_fin"].widget.attrs.update({"readonly": "readonly"})
        return f
