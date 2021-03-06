import { ICentroCostoByDeposito } from './../../models/Interfaces';
import { map } from 'rxjs/operators';
import { Response } from '@angular/http';
import { Observable } from 'rxjs';
import { Injectable } from '@angular/core';



import { ICentroCosto, IPresupuesto, IPeriodo } from '../../models/Interfaces';
import { BaseApiService } from '../base-api/base-api.service';

@Injectable()
export class CoreService {

  constructor(private http: BaseApiService) {
  }

  /* OBRAS */

  get_centro_costos_list() {
    return this.http.get(`/api/centro_costos/`)
      .pipe(map((r: Response) => {
        let r_json = r.json();
        return r_json['results'] as ICentroCosto[];
      }));
  }

  get_centro_costos_activos_list() {
    return this.http.get(`/api/centro_costos/activos/`)
      .pipe(map((r: Response) => {
        let r_json = r.json();
        return r_json['centros_costos'] as ICentroCosto[];
      }));
  }

  get_centro_costos_by_deposito(): Observable<Array<ICentroCostoByDeposito>> {
    return this.http.get(`/api/centro_costos/by-deposito/`)
      .pipe(map((r: Response) => {
        return r.json() as ICentroCostoByDeposito[];
      }));
  }

  get_centro_costos(id: number): Observable<ICentroCosto> {
    return this.http.get(`/api/centro_costos/${id}/`)
      .pipe(map((r: Response) => {
        return r.json() as ICentroCosto;
      }));
  }

  /* Periodo */

  get_periodos_list() {
    return this.http.get(`/api/periodos/`)
    .pipe(map((r: Response) => {
      let r_json = r.json();
      return r_json['results'] as IPeriodo[];
    }));
  }

}
