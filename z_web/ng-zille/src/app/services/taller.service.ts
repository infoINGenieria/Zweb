import { IEquipo } from '../models/Interfaces';
import { BaseApiService } from './base-api/base-api.service';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Response, URLSearchParams } from '@angular/http';
import 'rxjs/add/operator/map';


@Injectable()
export class TallerService {

  constructor(private http: BaseApiService) { }

  // Equipos
  /*
  this.f_ninterno,
      this.f_marca,
      this.f_modelo,
      this.f_tipo,
      this.f_dominio,
      this.f_anio,
      this.f_estado
      */
  get_equipos_list(page?, ninterno?, marca?, modelo?, tipo?, dominio?, anio?, estado?) {
    let myParams = new URLSearchParams();
    myParams.set('page', page || 1);
    myParams.set('n_interno', ninterno || '');
    myParams.set('marca', marca || '');
    myParams.set('modelo', modelo || '');
    myParams.set('equipo', tipo || '');
    myParams.set('dominio', dominio || '');
    myParams.set('año', anio || '');
    myParams.set('estado', estado || '');
    return this.http.get('/api/equipos/', myParams)
    .map((r: Response) => r.json());
  }

  get_equipo(pk: number): Observable<IEquipo> {
    return this.http.get(`/api/equipos/${pk}/`)
      .map((r: Response) => r.json() as IEquipo);
  }

  delete_equipo(equipo: IEquipo): Observable<IEquipo> {
    return this.http.delete(`/api/equipos/${equipo.id}/`)
    .map((res: Response) => res.json())
    .catch((error: any) => Observable.throw(error.json().detail || 'Error en el servidor'));
  }

  create_equipo(equipo: IEquipo): Observable<IEquipo> {
    const bodyString = JSON.stringify(equipo);
    return this.http.post(`/api/equipos/`, bodyString)
      .map((r: Response) => r.json() as IEquipo);
  }

  update_equipo(equipo: IEquipo): Observable<IEquipo> {
    const bodyString = JSON.stringify(equipo);
    return this.http.put(`/api/equipos/${equipo.id}`, bodyString)
      .map((r: Response) => r.json() as IEquipo);
  }

  get_familia_equipos() {
    return this.http.get('/api/familia_equipos/')
      .map((r: Response) => r.json());
  }

  set_baja_equipos(pk: number) {
    return this.http.post(`/api/equipos/${pk}/set-baja/`, {})
      .map((r: Response) => r.json());
  }
}
