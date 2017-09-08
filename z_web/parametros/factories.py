import factory

from parametros.models import Periodo


class PeriodoFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Periodo


