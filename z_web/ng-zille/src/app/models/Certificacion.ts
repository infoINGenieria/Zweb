import { ICertificacion, IPeriodo, ICertificacionItem, ICentroCosto } from './Interfaces';

export class Certificacion implements ICertificacion {
    pk?: number;
    periodo: IPeriodo;
    periodo_id: number;
    obra: ICentroCosto;
    obra_id: number;
    items: Array<ICertificacionItem>;
    total: number;
    total_sin_adicional: number;
    total_adicional: number;

    constructor(obj?) {
        if (obj) {
            this.pk = obj.pk;
            this.periodo = obj.periodo;
            this.periodo_id = obj.periodo_id;
            this.obra = obj.obra;
            this.obra_id = obj.obra_id;
            this.items = obj.items;
            this.total = obj.total;
            this.total_sin_adicional = obj.total_sin_adicional;
            this.total_adicional = obj.total_adicional;
        } else {
            this.pk = null;
            this.periodo = null;
            this.periodo_id = null;
            this.obra = null;
            this.obra_id = null;
            // this.items = [];
            this.total = 0;
            this.total_sin_adicional = 0;
            this.total_adicional = 0;
        }
    }
}
