import { ICentroCosto, IPeriodo } from './../models/Interfaces';
import { Observable } from 'rxjs/Rx';
import { BaseApiService } from './base-api/base-api.service';
import { Injectable } from '@angular/core';
import { Response } from '@angular/http';
import 'rxjs/add/operator/map';

@Injectable()
export class TableroService {

  constructor(private http: BaseApiService) { }

  get_data_table(centro_costo: ICentroCosto, periodo: IPeriodo): Observable<any> {
    return this.http.get(`/api/tablero/os/${centro_costo.id}/${periodo.pk}/`)
      .map((r: Response) => r.json());
  }

  get_graph_certificacion(centro_costo: ICentroCosto, periodo: IPeriodo): Observable<any> {
    return this.http.get(`/api/tablero/os/${centro_costo.id}/${periodo.pk}/graph_certificacion/`)
    .map((r: Response) => r.json());
  }

  get_graph_costo(centro_costo: ICentroCosto): Observable<any> {
    return this.http.get(`/api/tablero/os/${centro_costo.id}/graph_costo/`)
    .map((r: Response) => r.json());
  }
  get_graph_avance(centro_costo: ICentroCosto, periodo: IPeriodo): Observable<any> {
    return this.http.get(`/api/tablero/os/${centro_costo.id}/${periodo.pk}/graph_avance/`)
    .map((r: Response) => r.json());
  }

  get_graph_consolidado(centro_costo: ICentroCosto): Observable<any> {
    return this.http.get(`/api/tablero/os/${centro_costo.id}/consolidado/`)
    .map((r: Response) => r.json());
  }
}
