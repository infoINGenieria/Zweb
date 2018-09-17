from django.db import models


class EquipoManager(models.Manager):
    def actives(self):
        return super(EquipoManager, self).get_queryset().filter(
            fecha_baja__isnull=True
        )

    def actives_as_of(self, date=None):
        if date:
            return super(EquipoManager, self).get_queryset().filter(
                models.Q(fecha_baja__isnull=True) | models.Q(fecha_baja__gt=date)
            )
        else:
            return self.actives()

    def actives_in_cost(self, date=None):
        if date:
            qs = self.actives_as_of(date)
        else:
            qs = self.actives()
        return qs.filter(excluir_costos_taller=False)
