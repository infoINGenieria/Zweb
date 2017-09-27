import { BaseApiService } from './../base-api/base-api.service';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { Response} from '@angular/http';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { Presupuesto } from './../../models/Presupuesto';
import { TipoItemPresupuesto } from './../../models/TipoItemPresupuesto';
import { Revision } from './../../models/Revision';

@Injectable()
export class PresupuestosService {

  constructor(private http: BaseApiService) {
  }

  get_presupuestos(): Observable<Presupuesto[]> {
    return this.http.get(`/api/presupuestos/`)
      .map((r: Response) => {
        let r_json = r.json();
        let results = r_json['results'] as Presupuesto[];
        return results;
      });
  }

  get_revision(presu_pk: number, version: number): Observable<Revision> {
    return this.http.get(`/api/presupuestos/${presu_pk}/v/${version}`)
      .map((r: Response) => r.json() as Revision);
  }

  /* Tipo de Item de presupuesto */
  get_tipo_items(): Observable<TipoItemPresupuesto[]> {
    return this.http.get(`/api/tipo_items/`)
      .map((r: Response) => r.json()['results'] as TipoItemPresupuesto[]);
  }

  create_tipo_item(nombre: string): Observable<TipoItemPresupuesto[]> {
    let bodyString = JSON.stringify({'nombre': nombre});

    return this.http.post(`/api/tipo_items/`, bodyString)
      .map((res: Response) => res.json());
  }

  update_tipo_item(item: TipoItemPresupuesto): Observable<TipoItemPresupuesto[]> {
    let bodyString = JSON.stringify({'nombre': item.nombre});

    return this.http.put(`/api/tipo_items/${item.pk}`, bodyString)
      .map((res: Response) => res.json());
  }

  delete_tipo_item(item: TipoItemPresupuesto): Observable<TipoItemPresupuesto[]> {

    return this.http.delete(`/api/tipo_items/${item.pk}`)
      .map((res: Response) => res.json());
  }
}
