from django.db import models


class ValoresManager(models.Manager):
    def vigente(self, equipo, periodo):
        return super(ValoresManager, self).get_queryset().filter(
            equipo=equipo,
            valido_desde__fecha_inicio__lte=periodo.fecha_inicio
        ).order_by('-valido_desde__fecha_inicio').first()
