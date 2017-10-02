export interface MenuEntry {
    name: string;
    icon: string;
    url: string;
    section: string;
    btn_class: string;
}

export interface IPresupuesto {
    pk?: number;
    centro_costo_id: number;
    fecha: Date;
    aprobado: boolean;
    vigente: number;
    centro_costo: ICentroCosto;
}

export interface ICentroCosto {
    id: number;
    codigo: string;
    obra: string;
    lugar: string;
    plazo: string;
    responsable: string;
    unidad_negocio: string;
}

export interface IRevision {
    pk?: number;
    presupuesto: IPresupuesto;
    fecha: Date;
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
    precio_venta_dolar: number;

    items: Array<IItemPresupuesto>;
}

export interface IItemPresupuesto {
    pk?: number;
    tipo: ITipoItemPresupuesto;
    pesos: number;
    dolares: number;
    observaciones?: string;
    indirecto: boolean;

}

export interface ITipoItemPresupuesto {
    pk?: number;
    nombre: string;
}
