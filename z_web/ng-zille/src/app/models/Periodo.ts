import { IPeriodo } from './Interfaces';

import * as moment from 'moment';

export class Periodo implements IPeriodo {
    pk?: number;
    descripcion: string;
    fecha_inicio: string;
    fecha_fin: string;

    constructor(obj?) {
        if (obj) {
            this.pk = obj.pk;
            this.descripcion = obj.descripcion;
            this.fecha_fin = obj.fecha_fin;
            this.fecha_inicio = obj.fecha_inicio;
        } else {
            this.pk = null;
            this.descripcion = '';
            this.fecha_fin = null;
            this.fecha_inicio = null;
        }
    }

    fecha_inicio_obj() {
        if (this.fecha_inicio) {
            return moment(this.fecha_inicio, 'DD/MM/YYYY');
        }
        return null;
    }

    fecha_fin_obj() {
        if (this.fecha_fin) {
            return moment(this.fecha_fin, 'DD/MM/YYYY');
        }
        return null;
    }
}
