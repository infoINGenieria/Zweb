import { ICentroCosto, IPeriodo, ITableroControlEmitido } from '../models/Interfaces';
import { Observable } from 'rxjs';
import { BaseApiService } from './base-api/base-api.service';
import { Injectable } from '@angular/core';
import { Response } from '@angular/http';

import { map } from 'rxjs/operators';

@Injectable()
export class TableroService {

  constructor(private http: BaseApiService) { }

  get_data_table(centro_costo: ICentroCosto, periodo: IPeriodo): Observable<any> {
    return this.http.get(`/api/tablero/os/${centro_costo.id}/${periodo.pk}/`)
      .pipe(map((r: Response) => r.json()));
  }

  get_graph_certificacion(centro_costo: ICentroCosto, periodo: IPeriodo): Observable<any> {
    return this.http.get(`/api/tablero/os/${centro_costo.id}/${periodo.pk}/graph_certificacion/`)
    .pipe(map((r: Response) => r.json()));
  }

  get_graph_costo(centro_costo: ICentroCosto, periodo: IPeriodo): Observable<any> {
    return this.http.get(`/api/tablero/os/${centro_costo.id}/${periodo.pk}/graph_costo/`)
    .pipe(map((r: Response) => r.json()));
  }
  get_graph_avance(centro_costo: ICentroCosto, periodo: IPeriodo): Observable<any> {
    return this.http.get(`/api/tablero/os/${centro_costo.id}/${periodo.pk}/graph_avance/`)
    .pipe(map((r: Response) => r.json()));
  }

  get_graph_consolidado(centro_costo: ICentroCosto, periodo: IPeriodo): Observable<any> {
    return this.http.get(`/api/tablero/os/${centro_costo.id}/${periodo.pk}/consolidado/`)
    .pipe(map((r: Response) => r.json()));
  }

  emitir_tablero(tablero: ITableroControlEmitido): Observable<ITableroControlEmitido> {
    const bodyString = JSON.stringify(tablero);
    return this.http.post(`/api/centro_costos_emitidos/`, bodyString)
      .pipe(map((r: Response) => r.json() as ITableroControlEmitido));
  }
}
