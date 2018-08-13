import { IAsistencia, IRegistroAsistencia, IEquipo, ICentroCosto } from './Interfaces';


export class RegistroAsistencia implements IRegistroAsistencia {
    pk?: number;
    equipo: IEquipo;
    equipo_id: number;
    centro_costo: ICentroCosto;
    centro_costo_id: number;
    asistencia_id?: number;

    constructor(obj?) {
        if (obj) {
            this.pk = obj.pk;
            this.equipo = obj.equipo;
            this.equipo_id = obj.equipo_id;
            this.centro_costo = obj.centro_costo;
            this.centro_costo_id = obj.centro_costo_id;
            this.asistencia_id = obj.asistencia_id;
        } else {
            this.equipo = null;
            this.equipo_id = null;
            this.centro_costo = null;
            this.centro_costo_id = null;
            this.asistencia_id = null;
        }
    }

}
