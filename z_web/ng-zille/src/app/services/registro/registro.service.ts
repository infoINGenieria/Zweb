
import {throwError as observableThrowError,  Observable } from 'rxjs';
import { Certificacion } from '../../models/Certificacion';
import { ICertificacion } from '../../models/Interfaces';
import { Response, URLSearchParams } from '@angular/http';
import { BaseApiService } from '../base-api/base-api.service';
import { Injectable } from '@angular/core';

@Injectable()
export class RegistroService {

  constructor(private http: BaseApiService) { }

  get_certificacion_list(centro_costo?, periodo?) {
    let myParams = new URLSearchParams();
    myParams.set('obra', centro_costo || '');
    myParams.set('periodo', periodo || '');
    return this.http.get('/api/certificaciones/', myParams)
      .map((r: Response) => {
        let r_json = r.json();
        return r_json['results'] as ICertificacion[];
      });
  }

  get_certificacion(pk: number): Observable<ICertificacion> {
    return this.http.get(`/api/certificaciones/${pk}/`)
      .map((r: Response) => r.json() as ICertificacion);
  }

  delete_certificacion(certificacion: ICertificacion): Observable<ICertificacion> {
    return this.http.delete(`/api/certificaciones/${certificacion.pk}/`)
    .map((res: Response) => res.json())
    .catch((error: any) => observableThrowError(error.json().detail || 'Server error'));
  }

  create_certificacion(certificacion: ICertificacion): Observable<ICertificacion> {
    const bodyString = JSON.stringify(certificacion);
    return this.http.post(`/api/certificaciones/`, bodyString)
      .map((r: Response) => r.json() as ICertificacion);
  }

  update_certificacion(certificacion: ICertificacion): Observable<ICertificacion> {
    const bodyString = JSON.stringify(certificacion);
    return this.http.put(`/api/certificaciones/${certificacion.pk}`, bodyString)
      .map((r: Response) => r.json() as ICertificacion);
  }
}
