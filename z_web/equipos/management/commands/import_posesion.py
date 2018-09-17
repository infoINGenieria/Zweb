import os
import csv
from decimal import Decimal as D

from django.core.management.base import BaseCommand, CommandError

from core.models import Equipos
from parametros.models import Periodo
from equipos.models import (
    PosesionParametros, PosesionValores
)

def _d(val):
    if not val:
        return D(0)
    return D(val.replace(',', '.'))


class Command(BaseCommand):
    help = 'Importar valores y parametros de posesion'

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

            posesion_param, _ = PosesionParametros.objects.get_or_create(
                equipo=equipo,
                valido_desde=periodo,
                posesion_hs=int(row[1]),
                precio_del_activo=_d(row[3]),
                residual=_d(row[4])
            )
            posesion_valor, _ = PosesionValores.objects.get_or_create(
                equipo=equipo,
                valido_desde=periodo,
                seguros=_d(row[5]),
                ruta=_d(row[6]),
                vtv=_d(row[7]),
                certificacion=_d(row[8]),
                habilitaciones=_d(row[9]),
                rsv=_d(row[10]),
                vhf=_d(row[11]),
                impuestos=_d(row[12]),
                )
            print("{} -> Costo total $/m: {} | Planilla: {}".format(
                equipo,
                posesion_valor.costo_total_pesos_hora,
                row[13]
            ))
