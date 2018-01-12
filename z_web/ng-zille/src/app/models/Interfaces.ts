export interface MenuEntry {
    name: string;
    icon: string;
    url: string;
    section: string;
    btn_class: string;
    link: boolean;
}

export interface IPresupuesto {
    pk?: number;
    centro_costo_id: number;
    fecha: string;
    fecha_vigente: Date;
    aprobado: boolean;
    vigente: number;
    venta_actual: number;
    venta_revision_anterior: number;
    versiones: Array<number>;
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
    fecha: string;
    version: number;
    valor_dolar: number;

    // venta
    venta_contractual_b0: number;
    ordenes_cambio: number;
    reajustes_precio: number;
    reclamos_reconocidos: number;

    contingencia: number;
    estructura_no_ree: number;
    aval_por_anticipos: number;
    seguro_caucion: number;
    aval_por_cumplimiento_contrato: number;
    aval_por_cumplimiento_garantia: number;
    seguro_5: number;
    imprevistos: number;
    impuestos_ganancias: number;
    sellado: number;
    ingresos_brutos: number;
    impuestos_cheque: number;
    costo_financiero: number;

    items: Array<IItemPresupuesto>;
}

export interface IItemPresupuesto {
    pk?: number;
    tipo: ICostoTipo;
    pesos: number;
    dolares: number;
    observaciones?: string;
    indirecto: boolean;

}

export interface ICostoTipo {
    pk?: number;
    nombre: string;
}

export interface ICertificacionItem {
    pk?: number;
    concepto: string;
    monto: number;
    observaciones?: string;
}

export interface IPeriodo {
    pk?: number;
    descripcion: string;
    fecha_inicio: string;
    fecha_fin: string;

    fecha_inicio_obj(): any;
    fecha_fin_obj(): any;
}

export interface ICertificacion {
    pk?: number;
    periodo: IPeriodo;
    periodo_id: number;
    obra: ICentroCosto;
    obra_id: number;
    items: Array<ICertificacionItem>;
    total: number;
    total_sin_adicional: number;
    total_adicional: number;
}

export interface IAvanceObra {
    pk?: number;
    periodo: IPeriodo;
    periodo_id: number;
    centro_costo: ICentroCosto;
    centro_costo_id: number;
    avance: number;
    observacion: string;
}

export interface IAvanceObraThin {
    pk?: number;
    periodo_id: number;
    centro_costo_id: number;
    avance: number;
    observacion: string;
}

export interface IItemProyeccionAvanceObra {
    pk?: number;
    periodo: number;
    avance: number;
}

export interface IProyeccionAvanceObra {
    pk?: number;
    periodo: IPeriodo;
    periodo_id: number;
    centro_costo: ICentroCosto;
    centro_costo_id: number;
    observacion: string;
    es_base: boolean;
    base_numero: number;
    items: Array<IItemProyeccionAvanceObra>;
    avance_real: Array<IAvanceObraThin>;
    base_vigente: number;
}

export interface ICertificacionThin {
    pk?: number;
    periodo_id: number;
    centro_costo_id: number;
    total: number;
}

export interface IItemProyeccionCertificacion {
    pk?: number;
    periodo: number;
    monto: number;
}

export interface IProyeccionCertificacion {
    pk?: number;
    periodo: IPeriodo;
    periodo_id: number;
    centro_costo: ICentroCosto;
    centro_costo_id: number;
    observacion: string;
    es_base: boolean;
    base_numero: number;
    items: Array<IItemProyeccionCertificacion>;
    certificacion_real: Array<ICertificacionThin>;
    base_vigente: number;
}


export interface ICostoThin {
    pk?: number;
    periodo_id: number;
    centro_costo_id: number;
    tipo_costo_id: number;
    monto_total: number;
}

export interface IItemProyeccionCosto {
    pk?: number;
    periodo: number;
    tipo_costo: number;
    monto: number;
}

export interface IProyeccionCosto {
    pk?: number;
    periodo: IPeriodo;
    periodo_id: number;
    centro_costo: ICentroCosto;
    centro_costo_id: number;
    tipo_costo: ICostoTipo;
    tipo_costo_id: number;
    observacion: string;
    es_base: boolean;
    base_numero: number;
    items: Array<IItemProyeccionCosto>;
    costo_real: Array<ICostoThin>;
    periodos: Array<Number>;
    base_vigente: number;
}
