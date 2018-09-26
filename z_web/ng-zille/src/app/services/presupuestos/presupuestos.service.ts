
import {throwError as observableThrowError,  Observable } from 'rxjs';
import { BaseApiService } from '../base-api/base-api.service';
import { Injectable } from '@angular/core';
import { Response, URLSearchParams } from '@angular/http';
import { IPresupuesto, ICostoTipo, IRevision } from '../../models/Interfaces';
import { map } from 'rxjs/operators';

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
    return this.http.get(`/api/presupuestos/`, myParams).pipe(
      map((r: Response) => r.json()['results'] as IPresupuesto[])
    );
  }

  create_presupuesto(presupuesto: IPresupuesto): Observable<IPresupuesto> {
    const bodyString = JSON.stringify(presupuesto);
    return this.http.post(`/api/presupuestos/`, bodyString).pipe(
      map((r: Response) => r.json() as IPresupuesto)
    );
  }

  get_revision(presu_pk: number, version: number): Observable<IRevision> {
    return this.http.get(`/api/presupuestos/${presu_pk}/v/${version}/`)
      .pipe(map((r: Response) => r.json() as IRevision));
  }

  create_revision(revision: IRevision): Observable<IRevision> {
    const bodyString = JSON.stringify(revision);
    return this.http.post(`/api/presupuestos/${revision.presupuesto.pk}/v/`, bodyString)
      .pipe(map((res: Response) => res.json() as IRevision));
  }

  save_revision(revision: IRevision): Observable<IRevision> {
    const bodyString = JSON.stringify(revision);
    return this.http.put(`/api/presupuestos/${revision.presupuesto.pk}/v/${revision.version}/`, bodyString)
      .pipe(map((res: Response) => res.json() as IRevision));
  }

  delete_presupuesto(presupuesto: IPresupuesto): Observable<IPresupuesto> {
    return this.http.delete(`/api/presupuestos/${presupuesto.pk}/`)
      .pipe(map((res: Response) => res.json()));
  }


  /* Tipo de Item de presupuesto (aka Tipo de costo)*/
  get_tipo_items(): Observable<ICostoTipo[]> {
    return this.http.get(`/api/tipo_costos/`)
      .pipe(map((r: Response) => r.json()['results'] as ICostoTipo[]));
  }
}
