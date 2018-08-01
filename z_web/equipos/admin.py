from django.contrib import admin

from .models import (
    ParametrosGenerales,
    LubricantesParametros, LubricantesValores,
    TrenRodajeParametros, TrenRodajeValores,
    PosesionParametros, PosesionValores,
    ReparacionesParametros, ReparacionesValores,
    ManoObraValores,
    EquipoAlquiladoValores,
    CostoEquipoValores)


@admin.register(ParametrosGenerales)
class ParametrosGeneralesAdmin(admin.ModelAdmin):
    pass


@admin.register(LubricantesParametros)
class LubricantesParametrosAdmin(admin.ModelAdmin):
    pass


@admin.register(LubricantesValores)
class LubricantesValoresAdmin(admin.ModelAdmin):
    pass


@admin.register(TrenRodajeParametros)
class TrenRodajeParametrosAdmin(admin.ModelAdmin):
    pass


@admin.register(TrenRodajeValores)
class TrenRodajeValoresAdmin(admin.ModelAdmin):
    pass



@admin.register(PosesionParametros)
class PosesionParametrosAdmin(admin.ModelAdmin):
    pass


@admin.register(PosesionValores)
class PosesionValoresAdmin(admin.ModelAdmin):
    pass


@admin.register(ReparacionesParametros)
class ReparacionesParametrosAdmin(admin.ModelAdmin):
    pass


@admin.register(ReparacionesValores)
class ReparacionesValoresAdmin(admin.ModelAdmin):
    pass


@admin.register(ManoObraValores)
class ManoObraValoresAdmin(admin.ModelAdmin):
    pass


@admin.register(EquipoAlquiladoValores)
class EquipoAlquiladoValoresAdmin(admin.ModelAdmin):
    pass


@admin.register(CostoEquipoValores)
class CostoEquipoValoresAdmin(admin.ModelAdmin):
    pass
