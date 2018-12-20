import { IPosesionValores, IPeriodo, IEquipo, IPosesionParametros } from './Interfaces';

export class PosesionValores implements IPosesionValores {
    pk?: number;
    valido_desde: IPeriodo;
    valido_desde_id: number;
    equipo: IEquipo;
    equipo_id: number;
    seguros: number;
    ruta: number;
    vtv: number;
    certificacion: number;
    habilitaciones: number;
    rsv: number;
    vhf: number;
    impuestos: number;
    parametros: IPosesionParametros;
    costo_total_pesos_hora: number;
    costo_total_pesos_mes: number;

    constructor() {}

    costo_del_activo(precio_dolar: number) {
        try {
            const costo = (
                Number(this.parametros.precio_del_activo) - Number(this.parametros.residual_en_USD)
                ) * Number(precio_dolar) / Number(this.parametros.posesion_en_anios);
            return costo;
        } catch (ex) {
            console.log('Error en el calculo del activo', ex);
            return 0;
        }
    }

    total_impuestos_y_certificados() {
        try {
            let total = Number(this.seguros);
            total += Number(this.ruta);
            total += Number(this.vtv);
            total += Number(this.certificacion);
            total += Number(this.habilitaciones);
            total += Number(this.rsv);
            total += Number(this.vhf);
            total += Number(this.impuestos);
            total *= 12;
            return total;
        } catch(ex) {
            console.error('Error en la sumatoria de impuestos de posesión', ex);
            return 0;
        }

    }
    costo_anual(precio_dolar) {
        return this.costo_del_activo(precio_dolar) + this.total_impuestos_y_certificados();
    }

    costo_mensual(precio_dolar) {
        return this.costo_anual(precio_dolar) / 12;
    }

    costo_hora(precio_dolar, horas_anio) {
        return this.costo_anual(precio_dolar) / Number(horas_anio);
    }
  }

