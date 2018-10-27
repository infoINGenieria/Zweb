from django.apps import AppConfig
from django.db.models.signals import post_save



class EquiposConfig(AppConfig):
   name = 'equipos'
   verbose_name = 'Equipos'

   def ready(self):
        import equipos.signals  # noqa
