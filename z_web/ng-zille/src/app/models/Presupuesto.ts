import { Serializable } from './Serializable';

export class Presupuesto extends Serializable {
    pk?: number;
    centro_costo: string;
    fecha: Date = new Date();
    aprobado: boolean;
    vigente: number;

    constructor(obj?) {
        super();
        if (obj) {
            this.pk = obj.pk;
            this.centro_costo = obj.centro_costo.obra;
            this.fecha = obj.fecha;
            this.aprobado = obj.aprobado;
            this.vigente = obj.vigente;
        }
    }
}
