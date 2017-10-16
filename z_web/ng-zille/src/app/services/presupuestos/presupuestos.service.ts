import { BaseApiService } from './../base-api/base-api.service';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Rx';
import { Response, URLSearchParams } from '@angular/http';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { IPresupuesto, ITipoItemPresupuesto, IRevision } from './../../models/Interfaces';

@Injectable()
export class PresupuestosService {

  constructor(private http: BaseApiService) {
  }

  /* Presupuestos */
  get_presupuestos(centro_costo?, desde?, hasta?): Observable<IPresupuesto[]> {
    let myParams = new URLSearchParams();
    myParams.set('centro_costo', centro_costo || '');
    myParams.set('desde', desde || '');
    myParams.set('hasta', hasta || '');
    return this.http.get(`/api/presupuestos/`, myParams)
      .map((r: Response) => r.json()['results'] as IPresupuesto[]);
  }

  create_presupuesto(presupuesto: IPresupuesto): Observable<IPresupuesto> {
    const bodyString = JSON.stringify(presupuesto);
    return this.http.post(`/api/presupuestos/`, bodyString)
      .map((r: Response) => r.json() as IPresupuesto);
  }

  get_revision(presu_pk: number, version: number): Observable<IRevision> {
    return this.http.get(`/api/presupuestos/${presu_pk}/v/${version}/`)
      .map((r: Response) => r.json() as IRevision);
  }

  create_revision(revision: IRevision): Observable<IRevision> {
    const bodyString = JSON.stringify(revision);
    return this.http.post(`/api/presupuestos/${revision.presupuesto.pk}/v/`, bodyString)
      .map((res: Response) => res.json() as IRevision);
  }

  save_revision(revision: IRevision): Observable<IRevision> {
    const bodyString = JSON.stringify(revision);
    return this.http.put(`/api/presupuestos/${revision.presupuesto.pk}/v/${revision.version}/`, bodyString)
      .map((res: Response) => res.json() as IRevision);
  }

  delete_presupuesto(presupuesto: IPresupuesto): Observable<IPresupuesto> {
    return this.http.delete(`/api/presupuestos/${presupuesto.pk}/`)
      .map((res: Response) => res.json())
      .catch((error: any) => Observable.throw(error.json().detail || 'Server error'));
  }


  /* Tipo de Item de presupuesto */
  get_tipo_items(): Observable<ITipoItemPresupuesto[]> {
    return this.http.get(`/api/tipo_items/`)
      .map((r: Response) => r.json()['results'] as ITipoItemPresupuesto[]);
  }

  create_tipo_item(nombre: string): Observable<ITipoItemPresupuesto[]> {
    const bodyString = JSON.stringify({'nombre': nombre});

    return this.http.post(`/api/tipo_items/`, bodyString)
      .map((res: Response) => res.json());
  }

  update_tipo_item(item: ITipoItemPresupuesto): Observable<ITipoItemPresupuesto[]> {
    const bodyString = JSON.stringify({'nombre': item.nombre});

    return this.http.put(`/api/tipo_items/${item.pk}/`, bodyString)
      .map((res: Response) => res.json());
  }

  delete_tipo_item(item: ITipoItemPresupuesto): Observable<ITipoItemPresupuesto[]> {

    return this.http.delete(`/api/tipo_items/${item.pk}/`)
      .map((res: Response) => res.json())
      .catch((error: any) => Observable.throw(error.json().detail || 'Server error'));
  }
}
