import logging

from django.core.exceptions import ObjectDoesNotExist

from core.models import Equipos
from parametros.models import Periodo
from equipos.models import (
    LubricantesParametros,
    LubricantesParametrosItem,
    LubricantesValores,
    LubricantesValoresItem,
    TrenRodajeParametros,
    TrenRodajeValores,
    PosesionParametros,
    PosesionValores,
    ReparacionesParametros,
    ReparacionesValores,
    EquipoAlquiladoValores,
    CostoEquipoValores
)

logger = logging.getLogger(__name__)


def copy_cost_structure(equipo_target_id, equipo_from_id):
    target = Equipos.objects.get(pk=equipo_target_id)
    copy_from = Equipos.objects.get(pk=equipo_from_id)

    def clone_costo(obj, equipo_target):
        obj.pk = None
        obj.equipo = equipo_target
        obj.save()

    # copio todos los parámetros
    # lubricantes
    # Obtengo los valores para determinar el periodo
    try:
        lubri_valores_orig = LubricantesValores.objects.vigente_actual(copy_from)
        # Creo una copia de los parametros y sus items
        lubri_parametros_orig = lubri_valores_orig.mis_parametros
        lubri_parametros_new = LubricantesParametros.objects.create(
            equipo=target,
            valido_desde=lubri_parametros_orig.valido_desde,
            hp=lubri_parametros_orig.hp
        )
        for item_param in lubri_parametros_orig.items_lubricante.all():
            LubricantesParametrosItem.objects.create(
                parametro=lubri_parametros_new,
                item=item_param.item,
                cambios_por_anio=item_param.cambios_por_anio,
                volumen_por_cambio=item_param.volumen_por_cambio
            )
        # Ahora creamos el nuevo valor y todos los items
        lubri_valores_new = LubricantesValores.objects.create(
            equipo=target,
            valido_desde=lubri_valores_orig.valido_desde)

        for valor_item in lubri_valores_orig.valores.all():
            LubricantesValoresItem.objects.create(
                valor=lubri_valores_new,
                item=valor_item.item,
                valor_unitario=valor_item.valor_unitario
            )
    except ObjectDoesNotExist as ex:
        logger.error("Error al copiar costos de lubricantes")
        logger.error(ex)

    for costos_model in (TrenRodajeValores, PosesionValores, ReparacionesValores):
        try:
            valor_vigente = costos_model.objects.vigente_actual(copy_from)
            clone_costo(valor_vigente.mis_parametros, target)
            clone_costo(valor_vigente, target)
        except ObjectDoesNotExist as ex:
            logger.error("Error al copiar costos: %s", costos_model)
            logger.error(ex)

    # # Costo equipo
    try:
        costo_equipo = CostoEquipoValores.objects.vigente_actual(copy_from)
        clone_costo(costo_equipo, target)
    except ObjectDoesNotExist:
        CostoEquipoValores.objects.create(
            equipo=target,
            valido_desde=Periodo.con_parametros_costos.last(),
            markup=100
        )

