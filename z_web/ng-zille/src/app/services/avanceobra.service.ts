import { ICentroCosto, IPeriodo, IAvanceObra } from '../models/Interfaces';
import { Observable } from 'rxjs';
import { BaseApiService } from './base-api/base-api.service';
import { Injectable } from '@angular/core';
import { Response, URLSearchParams } from '@angular/http';
import 'rxjs/add/operator/map';

@Injectable()
export class AvanceObraService {

  constructor(private http: BaseApiService) { }

  // Avance de obra real

  get_avance_obra_list(centro_costo?) {
    let myParams = new URLSearchParams();
    myParams.set('centro_costo', centro_costo || '');
    return this.http.get('/api/avanceobra/', myParams)
    .map((r: Response) => {
      let r_json = r.json();
      return r_json['results'] as IAvanceObra[];
    });
  }

  get_avance_obra(pk: number): Observable<IAvanceObra> {
    return this.http.get(`/api/avanceobra/${pk}/`)
      .map((r: Response) => r.json() as IAvanceObra);
  }

  delete_avance_obra(avance_obra: IAvanceObra): Observable<IAvanceObra> {
    return this.http.delete(`/api/avanceobra/${avance_obra.pk}/`)
    .map((res: Response) => res.json())
    .catch((error: any) => Observable.throw(error.json().detail || 'Error en el servidor'));
  }

  create_avance_obra(avance_obra: IAvanceObra): Observable<IAvanceObra> {
    const bodyString = JSON.stringify(avance_obra);
    return this.http.post(`/api/avanceobra/`, bodyString)
      .map((r: Response) => r.json() as IAvanceObra);
  }

  update_avance_obra(avance_obra: IAvanceObra): Observable<IAvanceObra> {
    const bodyString = JSON.stringify(avance_obra);
    return this.http.put(`/api/avanceobra/${avance_obra.pk}`, bodyString)
      .map((r: Response) => r.json() as IAvanceObra);
  }
}
