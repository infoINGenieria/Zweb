import { IItemPresupuesto, ITipoItemPresupuesto } from './Interfaces';


export class ItemPresupuesto implements IItemPresupuesto {
    pk?: number;
    tipo: ITipoItemPresupuesto;
    pesos: number;
    dolares: number;
    observaciones?: string;
    indirecto: boolean;

    constructor(obj?) {
        if (obj) {
            this.pk = obj.pk;
            this.pesos = obj.pesos;
            this.dolares = obj.dolares;
            this.observaciones = obj.observaciones;
            this.tipo = obj.tipo;
            this.indirecto = obj.indirecto;
        } else {
            this.pesos = 0;
            this.dolares = 0;
            this.tipo = null;
            this.indirecto = false;
        }
    }

    /* peso_dolar(valor_dolar: number): number {
        const calc = Number(this.dolares) * valor_dolar;
        return calc;
    }

    total_item(valor_dolar: number): number {
        return Number(this.pesos) + this.peso_dolar(valor_dolar);
    } */
}
