from django.db.models.signals import post_save
from django.dispatch import receiver

from equipos.models import (
    CostoEquipoValores, TotalFlota, ManoObraValores,
    BaseParametrosCostos
)


# @receiver(post_save, sender=CostoEquipoValores)
@receiver(post_save, sender=ManoObraValores)
def update_total_tropa(sender, instance, **kwargs):
    periodo = instance.valido_desde
    flota, _ = TotalFlota.objects.get_or_create(valido_desde=periodo)
    flota.calcular_total_flota()


# @receiver(post_save, sender=BaseParametrosCostos.__subclasses__())
def actualizar_costos_equipo(sender, instance, **kwargs):
    if sender == CostoEquipoValores:
        return
    valor = CostoEquipoValores.objects.filter(
        equipo=instance.equipo,
        valido_desde__fecha_inicio__gte=instance.valido_desde.fecha_inicio
    ).order_by('valido_desde__fecha_inicio').first()
    if valor:
        valor.calcular()


# binding
for sub_class in BaseParametrosCostos.__subclasses__():
   post_save.connect(actualizar_costos_equipo, sender=sub_class)
