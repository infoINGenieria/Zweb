import { Certificacion } from './../../models/Certificacion';
import { Observable } from 'rxjs/Observable';
import { ICertificacion } from './../../models/Interfaces';
import { Response, URLSearchParams } from '@angular/http';
import { BaseApiService } from './../base-api/base-api.service';
import { Injectable } from '@angular/core';

@Injectable()
export class RegistroService {

  constructor(private http: BaseApiService) { }

  get_certificacion_real_list(centro_costo?, periodo?) {
    let myParams = new URLSearchParams();
    myParams.set('obra', centro_costo || '');
    myParams.set('periodo', periodo || '');
    return this.http.get('/api/certificaciones_real/', myParams)
      .map((r: Response) => {
        let r_json = r.json();
        return r_json['results'] as ICertificacion[];
      });
  }

  get_certificacion_real(pk: number): Observable<ICertificacion> {
    return this.http.get(`/api/certificaciones_real/${pk}/`)
      .map((r: Response) => r.json() as ICertificacion);
  }

  delete_certificacion_real(certificacion: ICertificacion): Observable<ICertificacion> {
    return this.http.delete(`/api/certificaciones_real/${certificacion.pk}/`)
    .map((res: Response) => res.json())
    .catch((error: any) => Observable.throw(error.json().detail || 'Server error'));
  }

  create_certificacion_real(certificacion_real: ICertificacion): Observable<ICertificacion> {
    const bodyString = JSON.stringify(certificacion_real);
    return this.http.post(`/api/certificaciones_real/`, bodyString)
      .map((r: Response) => r.json() as ICertificacion);
  }

  update_certificacion_real(certificacion_real: ICertificacion): Observable<ICertificacion> {
    const bodyString = JSON.stringify(certificacion_real);
    return this.http.put(`/api/certificaciones_real/${certificacion_real.pk}`, bodyString)
      .map((r: Response) => r.json() as ICertificacion);
  }

  get_certificacion_proyeccion_list(centro_costo?, periodo?) {
    let myParams = new URLSearchParams();
    myParams.set('obra', centro_costo || '');
    myParams.set('periodo', periodo || '');
    return this.http.get('/api/certificaciones_proyeccion/', myParams)
      .map((r: Response) => {
        let r_json = r.json();
        return r_json['results'] as ICertificacion[];
      });
  }

  get_certificacion_proyeccion(pk: number): Observable<ICertificacion> {
    return this.http.get(`/api/certificaciones_proyeccion/${pk}/`)
      .map((r: Response) => r.json() as ICertificacion);
  }

  delete_certificacion_proyeccion(certificacion: ICertificacion): Observable<ICertificacion> {
    return this.http.delete(`/api/certificaciones_proyeccion/${certificacion.pk}/`)
    .map((res: Response) => res.json())
    .catch((error: any) => Observable.throw(error.json().detail || 'Server error'));
  }

  create_certificacion_proyeccion(certificacion_proyeccion: ICertificacion): Observable<ICertificacion> {
    const bodyString = JSON.stringify(certificacion_proyeccion);
    return this.http.post(`/api/certificaciones_proyeccion/`, bodyString)
      .map((r: Response) => r.json() as ICertificacion);
  }

  update_certificacion_proyeccion(certificacion_proyeccion: ICertificacion): Observable<ICertificacion> {
    const bodyString = JSON.stringify(certificacion_proyeccion);
    return this.http.put(`/api/certificaciones_proyeccion/${certificacion_proyeccion.pk}`, bodyString)
      .map((r: Response) => r.json() as ICertificacion);
  }

  get_certificacion_proyeccion_by_obra(obra_id: number): Observable<Certificacion[]> {
    return this.http.get(`/api/centro_costos/${obra_id}/certificaciones-proyecciones/`)
      .map((r: Response) => r.json() as Certificacion[]);
  }

  get_certificacion_real_by_obra(obra_id: number): Observable<Certificacion[]> {
    return this.http.get(`/api/centro_costos/${obra_id}/certificaciones-reales/`)
      .map((r: Response) => r.json() as Certificacion[]);
  }
}
