import { Serializable } from './Serializable';
import { Presupuesto } from './Presupuesto';
import { ItemPresupuesto } from './ItemPresupuesto';

export class Revision extends Serializable {
    pk?: number;
    presupuesto: Presupuesto;
    fecha: Date = new Date();
    version: number;
    valor_dolar: number;

    contingencia: number;
    estructura_no_ree: number;
    aval_por_anticipos: number;
    seguro_caucion: number;
    aval_por_cumplimiento_contrato: number;
    aval_por_cumplimiento_garantia: number;
    seguro_5: number;
    imprevistos: number;
    ganancias: number;
    impuestos_ganancias: number;
    sellado: number;
    ingresos_brutos: number;
    impuestos_cheque: number;
    costo_financiero: number;
    precio_venta: number;
    precio_venta_dolares: number;

    items: Array<ItemPresupuesto> = [];

    constructor(obj?) {
        super();
        if (obj) {
            this.pk = obj.pk;
            this.presupuesto = obj.presupuesto;
            this.fecha = obj.fecha;
            this.version = obj.version;
            this.valor_dolar = obj.valor_dolar;
            this.items = obj.items;
        }
    }

    total_pesos_items(): number {
        let total = 0;
        for (const item of this.items) {
          total += Number(item.pesos);
        }
        return total;
    }

    total_dolares_items(): number {
        let total = 0;
        for (const item of this.items) {
            total += Number(item.dolares);
        }
        return total;
    }

    total_items(): number {
        return this.total_pesos_items() + (this.total_dolares_items() * this.valor_dolar);
    }

    get_perc_sobre_venta(): number {
        let perc = this.aval_por_anticipos || 0;
        perc += this.seguro_caucion || 0;
        perc += this.aval_por_cumplimiento_contrato || 0;
        perc += this.aval_por_cumplimiento_garantia || 0;
        perc += this.seguro_5 || 0;
        perc += this.sellado || 0;
        perc += this.ingresos_brutos || 0;
        perc += this.impuestos_cheque || 0;
        perc = perc / 100;
        return perc;
    }

    get_perc_dividendo_venta(): number {
        let perc = this.contingencia || 0;
        perc += this.estructura_no_ree || 0;
        perc += this.imprevistos || 0;
        perc += this.ganancias || 0;
        perc += (this.ganancias * this.impuestos_ganancias) || 0;
        perc += this.costo_financiero || 0;
        perc = perc / 100;
        return perc;
    }
}
