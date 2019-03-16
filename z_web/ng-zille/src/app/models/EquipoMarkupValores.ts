import { IEquipoMarkupValores, IEquipo, IPeriodo } from './Interfaces';

export class EquipoMarkupValores implements IEquipoMarkupValores {
    pk?: number;
    equipo: IEquipo;
    equipo_id: number;
    valido_desde: IPeriodo;
    valido_desde_id: number;
    markup: number;
    costo_mensual_del_activo_calculado: number;
    costo_mensual_del_activo_con_mo_calculado: number;
    costo_equipo_calculado: number;
    costo_mensual_mo_logistico: number;
}
