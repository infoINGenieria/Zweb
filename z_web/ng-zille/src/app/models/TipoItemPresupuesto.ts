import { Serializable } from './Serializable';


export class TipoItemPresupuesto extends Serializable {
    pk?: number;
    nombre: string;

    constructor(obj?) {
        super();
        if (obj) {
            this.nombre = obj.nombre;
            this.pk = obj.pk;
        }
    }
}
