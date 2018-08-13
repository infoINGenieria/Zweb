import { IParametrosGenerales, IAsistencia } from '../models/Interfaces';
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

  get_equipos_activos_list() {
    return this.http.get('/api/equipos/activos-taller/')
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

  // PARAMETROS GENERALES

  get_parametros_generales_list(page?, valido_desde?) {
    let myParams = new URLSearchParams();
    myParams.set('page', page || 1);
    myParams.set('valido_desde', valido_desde || '');
    return this.http.get('/api/taller/parametros_generales/', myParams)
    .map((r: Response) => r.json());
  }

  get_parametros_generales(pk: number): Observable<IParametrosGenerales> {
    return this.http.get(`/api/taller/parametros_generales/${pk}/`)
      .map((r: Response) => r.json() as IParametrosGenerales);
  }

  delete_parametros_generales(parametros_generales: IParametrosGenerales): Observable<IParametrosGenerales> {
    return this.http.delete(`/api/taller/parametros_generales/${parametros_generales.pk}/`)
    .map((res: Response) => res.json())
    .catch((error: any) => Observable.throw(error.json().detail || 'Error en el servidor'));
  }

  create_parametros_generales(parametros_generales: IParametrosGenerales): Observable<IParametrosGenerales> {
    const bodyString = JSON.stringify(parametros_generales);
    return this.http.post(`/api/taller/parametros_generales/`, bodyString)
      .map((r: Response) => r.json() as IParametrosGenerales);
  }

  update_parametros_generales(parametros_generales: IParametrosGenerales): Observable<IParametrosGenerales> {
    const bodyString = JSON.stringify(parametros_generales);
    return this.http.put(`/api/taller/parametros_generales/${parametros_generales.pk}`, bodyString)
      .map((r: Response) => r.json() as IParametrosGenerales);
  }


  // ASISTENCIA

    get_asistencias_list(page?, desde?, hasta?) {
      let myParams = new URLSearchParams();
      myParams.set('page', page || 1);
      myParams.set('desde', desde || '');
      myParams.set('hasta', hasta || '');
      return this.http.get('/api/taller/asistencia/', myParams)
      .map((r: Response) => r.json());
    }

    get_asistencia(pk: number): Observable<IAsistencia> {
      return this.http.get(`/api/taller/asistencia/${pk}/`)
        .map((r: Response) => r.json() as IAsistencia);
    }

    delete_asistencia(asistencia: IAsistencia): Observable<IAsistencia> {
      return this.http.delete(`/api/taller/asistencia/${asistencia.pk}/`)
      .map((res: Response) => res.json())
      .catch((error: any) => Observable.throw(error.json().detail || 'Error en el servidor'));
    }

    create_asistencia(asistencia: IAsistencia): Observable<IAsistencia> {
      const bodyString = JSON.stringify(asistencia);
      return this.http.post(`/api/taller/asistencia/`, bodyString)
        .map((r: Response) => r.json() as IAsistencia);
    }

    update_asistencia(asistencia: IAsistencia): Observable<IAsistencia> {
      const bodyString = JSON.stringify(asistencia);
      return this.http.put(`/api/taller/asistencia/${asistencia.pk}`, bodyString)
        .map((r: Response) => r.json() as IAsistencia);
    }
}
