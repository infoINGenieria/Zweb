import { Response } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import { Injectable } from '@angular/core';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { ICentroCosto, IPresupuesto, IPeriodo } from './../../models/Interfaces';
import { BaseApiService } from './../base-api/base-api.service';

@Injectable()
export class CoreService {

  constructor(private http: BaseApiService) {
  }

  /* OBRAS */

  get_centro_costos_list() {
    return this.http.get(`/api/centro_costos/`)
      .map((r: Response) => {
        let r_json = r.json();
        return r_json['results'] as ICentroCosto[];
      });
  }

  get_centro_costos(id: number): Observable<ICentroCosto> {
    return this.http.get(`/api/centro_costos/${id}/`)
      .map((r: Response) => {
        return r.json() as ICentroCosto;
      });
  }

  /* Periodo */

  get_periodos_list() {
    return this.http.get(`/api/periodos/`)
    .map((r: Response) => {
      let r_json = r.json();
      return r_json['results'] as IPeriodo[];
    });
  }

}
