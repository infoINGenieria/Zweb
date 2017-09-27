import { Serializable } from './Serializable';
import { TipoItemPresupuesto } from './TipoItemPresupuesto';


export class ItemPresupuesto extends Serializable {
    pk?: number;
    tipo: TipoItemPresupuesto;
    pesos: number;
    dolares: number;
    observaciones?: string;

    constructor(obj?) {
        super();
        if (obj) {
            this.pesos = obj.pesos;
            this.dolares = obj.dolares;
            this.observaciones = obj.observaciones;
            this.tipo = obj.tipo;
        } else {
            this.pesos = 0;
            this.dolares = 0;
            this.tipo = null;
        }
    }

    peso_dolar(valor_dolar: number): number {
        const calc = Number(this.dolares) * valor_dolar;
        return calc;
    }

    total_item(valor_dolar: number): number {
        return Number(this.pesos) + this.peso_dolar(valor_dolar);
    }
}
