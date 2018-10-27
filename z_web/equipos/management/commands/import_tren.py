import os
import csv
from decimal import Decimal as D

from django.core.management.base import BaseCommand, CommandError

from core.models import Equipos
from parametros.models import Periodo
from equipos.models import (
    TrenRodajeParametros, TrenRodajeValores
)

def _d(val):
    if not val:
        return D(0)
    return D(val.replace(',', '.'))


class Command(BaseCommand):
    help = 'Importar valores y parametros de tren de rodaje'

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

            if not row[8]:
                tren_param, _ = TrenRodajeParametros.objects.get_or_create(
                    equipo=equipo,
                    valido_desde=periodo,
                    vida_util_neumatico=int(row[1]),
                    cantidad_neumaticos=int(row[2]),
                    medidas=row[4]
                    )
                tren_valor, _ = TrenRodajeValores.objects.get_or_create(
                    equipo=equipo,
                    valido_desde=periodo,
                    precio_neumatico=_d(row[5])
                )
            else:
                tren_param, _ = TrenRodajeParametros.objects.get_or_create(
                    equipo=equipo,
                    valido_desde=periodo,
                    factor_basico=_d(row[8]),
                    impacto=_d(row[9]),
                    abracion=_d(row[10]),
                    z=_d(row[11])
                )
                tren_valor, _ = TrenRodajeValores.objects.get_or_create(
                    equipo=equipo,
                    valido_desde=periodo,
                    precio_neumatico=D(0)
                )
            print("{} -> Costo total $/m: {} | Planilla: {}".format(
                equipo,
                tren_valor.costo_total_pesos_hora,
                row[15]
            ))
