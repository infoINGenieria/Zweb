import os
import csv
from decimal import Decimal as D

from django.core.management.base import BaseCommand, CommandError

from core.models import Equipos
from parametros.models import Periodo
from equipos.models import (
    LubricantesParametros, LubricantesValores, LubricantesParametrosItem, LubricantesValoresItem,
    LubricanteItem
)

def _d(val):
    if not val:
        return D(0)
    return D(val.replace(',', '.'))


class Command(BaseCommand):
    help = 'Importar valores y parametros de lubricantes / fluidos hidráulicos'

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
            else:
                print(equipo)
            lubri_param, _ = LubricantesParametros.objects.get_or_create(
                equipo=equipo, valido_desde=periodo, hp=_d(row[1]))
            lubri_valor, _ = LubricantesValores.objects.get_or_create(
                    equipo=equipo, valido_desde=periodo
                )
            index = 2
            for item in LubricanteItem.objects.order_by('pk'):
                # primero determinamos si tenemos un valor distinto de cero
                cambios_por_anio = _d(row[index])
                index += 1
                volumen = 1
                if not item.es_filtro:
                    volumen = _d(row[index])
                    index += 1
                valor = _d(row[index])
                index += 1

                if any((cambios_por_anio, valor, )):
                    LubricantesParametrosItem.objects.get_or_create(
                        parametro=lubri_param, item=item, cambios_por_anio=cambios_por_anio,
                        volumen_por_cambio=volumen)

                    # valor
                    item_v, _ = LubricantesValoresItem.objects.get_or_create(
                        valor=lubri_valor,
                        item=item,
                        valor_unitario=valor
                    )
                    # item_v.save()
                    print("{} -> Cambios: {} | Vol: {} | Valor: {} | Costo: {} ({})".format(
                        item,
                        cambios_por_anio,
                        volumen,
                        valor,
                        item_v.costo_por_mes,
                        _d(row[index]),
                    ))
                index += 1
