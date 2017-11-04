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
}
