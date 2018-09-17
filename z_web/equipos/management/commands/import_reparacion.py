import os
import csv
from decimal import Decimal as D

from django.core.management.base import BaseCommand, CommandError

from core.models import Equipos
from parametros.models import Periodo
from equipos.models import (
    ReparacionesParametros, ReparacionesValores
)

def _d(val):
    if not val:
        return D(0)
    return D(val.replace(',', '.'))


class Command(BaseCommand):
    help = 'Importar valores y parametros de reserva para reparaciones'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)
        parser.add_argument('--id_periodo', type=int)

    def handle(self, *args, **options):

        if options['filename'] == None:
            raise CommandError("Debe especificar la ruta al archivo CSV.")

        # make sure file path resolves
        if not os.path.isfile(options['filename']):
            raise CommandError("El archivo especificado no existe.")

        periodo_id = options.get('id_periodo') or 40
        periodo = Periodo.objects.get(pk=periodo_id)
        dataReader = csv.reader(open(options["filename"]), delimiter=',', quotechar='"')
        for row in dataReader:
            # Buscamos equipo
            equipo = Equipos.objects.filter(n_interno=row[0]).first()
            if not equipo:
                print("%s no encontrado" % row[0])
                continue

            repara_param, _ = ReparacionesParametros.objects.get_or_create(
                equipo=equipo,
                valido_desde=periodo,
                factor_basico=_d(row[1]),
                multiplicador=_d(row[2])
            )
            repara_valor, _ = ReparacionesValores.objects.get_or_create(
                equipo=equipo,
                valido_desde=periodo,
            )
            print("{} -> Costo total $/m: {} | Planilla: {}".format(
                equipo,
                repara_valor.costo_total_pesos_hora,
                row[3]
            ))
