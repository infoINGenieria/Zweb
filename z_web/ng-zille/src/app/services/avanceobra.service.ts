import { ICentroCosto, IPeriodo, IAvanceObra } from './../models/Interfaces';
import { Observable } from 'rxjs/Rx';
import { BaseApiService } from './base-api/base-api.service';
import { Injectable } from '@angular/core';
import { Response, URLSearchParams } from '@angular/http';
import 'rxjs/add/operator/map';

@Injectable()
export class AvanceObraService {

  constructor(private http: BaseApiService) { }

  // Avance de obra proyección

  get_avance_obra_proyeccion_list(centro_costo?) {
    let myParams = new URLSearchParams();
    myParams.set('centro_costo', centro_costo || '');
    return this.http.get('/api/avanceobra_proyeccion/', myParams)
    .map((r: Response) => {
      let r_json = r.json();
      return r_json['results'] as IAvanceObra[];
    });
  }

  get_avance_obra_proyeccion(pk: number): Observable<IAvanceObra> {
    return this.http.get(`/api/avanceobra_proyeccion/${pk}/`)
      .map((r: Response) => r.json() as IAvanceObra);
  }

  delete_avance_obra_proyeccion(avance_obra: IAvanceObra): Observable<IAvanceObra> {
    return this.http.delete(`/api/avanceobra_proyeccion/${avance_obra.pk}/`)
    .map((res: Response) => res.json())
    .catch((error: any) => Observable.throw(error.json().detail || 'Server error'));
  }

  create_avance_obra_proyeccion(avance_obra_proyeccion: IAvanceObra): Observable<IAvanceObra> {
    const bodyString = JSON.stringify(avance_obra_proyeccion);
    return this.http.post(`/api/avanceobra_proyeccion/`, bodyString)
      .map((r: Response) => r.json() as IAvanceObra);
  }

  update_avance_obra_proyeccion(avance_obra_proyeccion: IAvanceObra): Observable<IAvanceObra> {
    const bodyString = JSON.stringify(avance_obra_proyeccion);
    return this.http.put(`/api/avanceobra_proyeccion/${avance_obra_proyeccion.pk}`, bodyString)
      .map((r: Response) => r.json() as IAvanceObra);
  }

  // Avance de obra real

  get_avance_obra_real_list(centro_costo?) {
    let myParams = new URLSearchParams();
    myParams.set('centro_costo', centro_costo || '');
    return this.http.get('/api/avanceobra_real/', myParams)
    .map((r: Response) => {
      let r_json = r.json();
      return r_json['results'] as IAvanceObra[];
    });
  }

  get_avance_obra_real(pk: number): Observable<IAvanceObra> {
    return this.http.get(`/api/avanceobra_real/${pk}/`)
      .map((r: Response) => r.json() as IAvanceObra);
  }

  delete_avance_obra_real(avance_obra: IAvanceObra): Observable<IAvanceObra> {
    return this.http.delete(`/api/avanceobra_real/${avance_obra.pk}/`)
    .map((res: Response) => res.json())
    .catch((error: any) => Observable.throw(error.json().detail || 'Server error'));
  }

  create_avance_obra_real(avance_obra_real: IAvanceObra): Observable<IAvanceObra> {
    const bodyString = JSON.stringify(avance_obra_real);
    return this.http.post(`/api/avanceobra_real/`, bodyString)
      .map((r: Response) => r.json() as IAvanceObra);
  }

  update_avance_obra_real(avance_obra_real: IAvanceObra): Observable<IAvanceObra> {
    const bodyString = JSON.stringify(avance_obra_real);
    return this.http.put(`/api/avanceobra_real/${avance_obra_real.pk}`, bodyString)
      .map((r: Response) => r.json() as IAvanceObra);
  }
}
