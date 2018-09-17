# encoding: utf-8
import os
import csv
from decimal import Decimal as D

from django.core.management.base import BaseCommand, CommandError

from core.models import Equipos


def _f(val):
    if val:
        val = float(val)
    return val


class Command(BaseCommand):
    help = 'Importar valores y parametros de tren de rodaje'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):

        if options['filename'] == None:
            raise CommandError("Debe especificar la ruta al archivo CSV.")

        # make sure file path resolves
        if not os.path.isfile(options['filename']):
            raise CommandError("El archivo especificado no existe.")

        dataReader = csv.reader(open(options["filename"]), delimiter=',', quotechar='"')
        for row in dataReader:
            # Buscamos equipo
            # Nº Int.	DOMINIO	EQUIPO	MARCA	FÁBRICA/ MODELO	CHASIS	AÑO
            try:
                equipo, created = Equipos.objects.get_or_create(
                    n_interno=row[0], defaults={
                        'dominio': row[1],
                        'equipo': row[2],
                        'marca': row[3],
                        'modelo': row[4],
                        'nro_serie': row[5],
                        'año': _f(row[6]) if row[6] else None
                    })
                if created:
                    print("NUEVO: {}".format(equipo))
            except Equipos.MultipleObjectsReturned:
                print("Equipo repetido: %s" % row[0])
