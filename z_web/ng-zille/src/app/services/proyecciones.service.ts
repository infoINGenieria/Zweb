import { Observable } from 'rxjs/Rx';
import { BaseApiService } from './base-api/base-api.service';
import { Injectable } from '@angular/core';
import { Response, URLSearchParams } from '@angular/http';
import 'rxjs/add/operator/map';

import {
  ICentroCosto, IPeriodo,
  IProyeccionAvanceObra, IItemProyeccionAvanceObra
} from './../models/Interfaces';

@Injectable()
export class ProyeccionesService {

  constructor(private http: BaseApiService) { }

  // proyección de Avance de obra

  get_proyeccion_avance_obra_list(centro_costo?, periodo?) {
    let myParams = new URLSearchParams();
    myParams.set('centro_costo', centro_costo || '');
    myParams.set('periodo', periodo || '');
    return this.http.get('/api/proyecciones/avance_obra/', myParams)
    .map((r: Response) => {
      let r_json = r.json();
      return r_json['results'] as IProyeccionAvanceObra[];
    });
  }

  get_proyeccion_avance_obra(pk: number): Observable<IProyeccionAvanceObra> {
    return this.http.get(`'/api/proyecciones/avance_obra/'${pk}/`)
      .map((r: Response) => r.json() as IProyeccionAvanceObra);
  }

  delete_proyeccion_avance_obra(avance_obra: IProyeccionAvanceObra): Observable<IProyeccionAvanceObra> {
    return this.http.delete(`/api/proyecciones/avance_obra/${avance_obra.pk}/`)
    .map((res: Response) => res.json())
    .catch((error: any) => Observable.throw(error.json().detail || 'Error en el servidor'));
  }

  create_avance_obra_proyeccion(avance_obra_proyeccion: IProyeccionAvanceObra): Observable<IProyeccionAvanceObra> {
    const bodyString = JSON.stringify(avance_obra_proyeccion);
    return this.http.post(`/api/proyecciones/avance_obra/`, bodyString)
      .map((r: Response) => r.json() as IProyeccionAvanceObra);
  }

  update_avance_obra_proyeccion(avance_obra_proyeccion: IProyeccionAvanceObra): Observable<IProyeccionAvanceObra> {
    const bodyString = JSON.stringify(avance_obra_proyeccion);
    return this.http.put(`/api/proyecciones/avance_obra/${avance_obra_proyeccion.pk}`, bodyString)
      .map((r: Response) => r.json() as IProyeccionAvanceObra);
  }

  hacer_vigente_avance_obra_proyeccion(avance_obra_proyeccion: IProyeccionAvanceObra): Observable<IProyeccionAvanceObra> {
    const bodyString = JSON.stringify(avance_obra_proyeccion);
    return this.http.post(`/api/proyecciones/avance_obra/${avance_obra_proyeccion.pk}/hacer-vigente/`, bodyString)
      .map((r: Response) => r.json() as IProyeccionAvanceObra);
  }
}
