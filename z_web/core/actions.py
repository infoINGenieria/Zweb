# encoding: utf-8
from django.utils import timezone


def set_baja_equipo(modeladmin, request, queryset):
    queryset.update(fecha_baja=timezone.now())
set_baja_equipo.short_description = "Dar de baja equipos"


def set_baja_obra(modeladmin, request, queryset):
    queryset.update(fecha_fin=timezone.now())
set_baja_obra.short_description = "Dar por finalizada la obra"
