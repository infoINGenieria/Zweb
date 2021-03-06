
import { IPeriodo, ILubricantesValores, ITrenRodajeValores, IPosesionValores,
   IReparacionesValores, IReparacionesParametros, IManoObraValores, IEquipoAlquiladoValores,
   IEquipoMarkupValores, ICentroCosto, IParametrosGenerales, IAsistencia  } from './../models/Interfaces';
import { IEquipo } from '../models/Interfaces';
import { BaseApiService } from './base-api/base-api.service';
import { Injectable } from '@angular/core';
import { Response, URLSearchParams, ResponseContentType, RequestOptions } from '@angular/http';
import { map } from 'rxjs/operators';
import {Observable} from 'rxjs/Observable';
import {Subject} from 'rxjs/Subject';

@Injectable()
export class TallerService {

  public tempStorage: any;
  public refreshListSubject: Subject<void> = new Subject<void>();  // Subject para notificar cuando se debe refrescar el listado

  constructor(private http: BaseApiService) { }

  get refreshListObservable(): Observable<void> {
    return this.refreshListSubject.asObservable();  // observador para refrescar el listado.
    // los componentes de listas deben subscribirse refrecando el listado, y desubscribirse al salir
  }

  // Equipos
  get_equipos_list(page?, equipo?, estado?, excluir_costos_taller?,
                   alquilado?, implica_mo_logistica?) {
    let myParams = new URLSearchParams();
    myParams.set('page', page || 1);
    myParams.set('equipo', equipo || '');
    myParams.set('estado', estado || '');
    myParams.set('excluir_costos_taller', excluir_costos_taller || '');
    myParams.set('alquilado', alquilado || '');
    myParams.set('implica_mo_logistica', implica_mo_logistica || '');
    return this.http.get('/api/equipos/', myParams)
    .pipe(
      map((r: Response) => r.json())
      );
  }

  get_equipos_activos_list() {
    return this.http.get('/api/equipos/activos-taller/')
    .pipe(
      map((r: Response) => r.json())
    );
  }

  get_equipos_alquilados_activos_list(): Observable<IEquipo[]> {
    return this.http.get('/api/equipos/alquilados-taller/')
    .pipe(
      map((r: Response) => r.json())
    );
  }

  get_equipos_propios_activos_list(): Observable<IEquipo[]> {
    return this.http.get('/api/equipos/propios-taller/')
    .pipe(
      map((r: Response) => r.json())
    );
  }

  get_equipo(pk: number): Observable<IEquipo> {
    return this.http.get(`/api/equipos/${pk}/`)
      .pipe(
        map(
          (r: Response) => r.json() as IEquipo
        )
      );
  }

  delete_equipo(equipo: IEquipo): Observable<IEquipo> {
    return this.http.delete(`/api/equipos/${equipo.id}/`)
    .pipe(map((res: Response) => res.json()));
  }

  create_equipo(equipo: IEquipo): Observable<IEquipo> {
    const bodyString = JSON.stringify(equipo);
    return this.http.post(`/api/equipos/`, bodyString)
      .pipe(map((r: Response) => r.json() as IEquipo));
  }

  update_equipo(equipo: IEquipo): Observable<IEquipo> {
    const bodyString = JSON.stringify(equipo);
    return this.http.put(`/api/equipos/${equipo.id}`, bodyString)
      .pipe(map((r: Response) => r.json() as IEquipo));
  }

  get_familia_equipos() {
    return this.http.get('/api/familia_equipos/')
      .pipe(map((r: Response) => r.json()));
  }

  set_baja_equipos(pk: number) {
    return this.http.post(`/api/equipos/${pk}/set-baja/`, {})
      .pipe(map((r: Response) => r.json()));
  }

  // PARAMETROS GENERALES

  get_parametros_generales_list(page?, valido_desde?) {
    let myParams = new URLSearchParams();
    myParams.set('page', page || 1);
    myParams.set('valido_desde', valido_desde || '');
    return this.http.get('/api/taller/parametros_generales/', myParams)
    .pipe(map((r: Response) => r.json()));
  }

  get_parametros_generales(pk: number): Observable<IParametrosGenerales> {
    return this.http.get(`/api/taller/parametros_generales/${pk}/`)
      .pipe(map((r: Response) => r.json() as IParametrosGenerales));
  }

  get_parametros_generales_latest(): Observable<IParametrosGenerales> {
    return this.http.get(`/api/taller/parametros_generales/latest/`)
      .pipe(map((r: Response) => r.json() as IParametrosGenerales));
  }

  delete_parametros_generales(parametros_generales: IParametrosGenerales): Observable<IParametrosGenerales> {
    return this.http.delete(`/api/taller/parametros_generales/${parametros_generales.pk}/`)
    .pipe(map((res: Response) => res.json()));
  }

  create_parametros_generales(parametros_generales: IParametrosGenerales): Observable<IParametrosGenerales> {
    const bodyString = JSON.stringify(parametros_generales);
    return this.http.post(`/api/taller/parametros_generales/`, bodyString)
      .pipe(map((r: Response) => r.json() as IParametrosGenerales));
  }

  update_parametros_generales(parametros_generales: IParametrosGenerales): Observable<IParametrosGenerales> {
    const bodyString = JSON.stringify(parametros_generales);
    return this.http.put(`/api/taller/parametros_generales/${parametros_generales.pk}`, bodyString)
      .pipe(map((r: Response) => r.json() as IParametrosGenerales));
  }


  // ASISTENCIA

    get_asistencias_list(page?, desde?, hasta?) {
      let myParams = new URLSearchParams();
      myParams.set('page', page || 1);
      myParams.set('desde', desde || '');
      myParams.set('hasta', hasta || '');
      return this.http.get('/api/taller/asistencia/', myParams)
      .pipe(map((r: Response) => r.json()));
    }

    get_asistencia(pk: number): Observable<IAsistencia> {
      return this.http.get(`/api/taller/asistencia/${pk}/`)
        .pipe(map((r: Response) => r.json() as IAsistencia));
    }

    delete_asistencia(asistencia: IAsistencia): Observable<IAsistencia> {
      return this.http.delete(`/api/taller/asistencia/${asistencia.pk}/`)
      .pipe(map((res: Response) => res.json()));
    }

    create_asistencia(asistencia: IAsistencia): Observable<IAsistencia> {
      const bodyString = JSON.stringify(asistencia);
      return this.http.post(`/api/taller/asistencia/`, bodyString)
        .pipe(map((r: Response) => r.json() as IAsistencia));
    }

    update_asistencia(asistencia: IAsistencia): Observable<IAsistencia> {
      const bodyString = JSON.stringify(asistencia);
      return this.http.put(`/api/taller/asistencia/${asistencia.pk}`, bodyString)
        .pipe(map((r: Response) => r.json() as IAsistencia));
    }

    get_reporte_asistencias_by_equipo(periodo: IPeriodo) {
      return this.http.get(`/api/taller/asistencia/reportes/equipos/${periodo.pk}/`)
      .pipe(map((r: Response) => r.json()));
    }

    download_reporte_asistencias_by_cc(periodo: IPeriodo, centro_costo: ICentroCosto): string {
      // solo devolver la URL, y abrirlo con window.open(service, "_blank");
      return `/api/taller/asistencia/reportes/cc/${periodo.pk}/${centro_costo.id}/`;
    }

    download_reporte_asistencias_summary(periodo: IPeriodo): string {
      // solo devolver la URL, y abrirlo con window.open(service, "_blank");
      return  `/api/taller/asistencia/reportes/summary/${periodo.pk}/`;
    }

    // COSTOS
    get_tablero_costo_taller(periodo: IPeriodo) {
      return this.http.get(`/api/taller/tablero/${periodo.pk}/`)
        .pipe(map( (r: Response) => r.json()));
    }

    get_tablero_costo_taller_detail(periodo: IPeriodo, equipo: IEquipo) {
      return this.http.get(`/api/taller/tablero/${periodo.pk}/${equipo.id}`)
        .pipe(map( (r: Response) => r.json()));
    }

    get_tablero_costo_taller_total_flota(periodo: IPeriodo) {
      return this.http.get(`/api/taller/tablero/${periodo.pk}/flota/?recalcular=True`)
        .pipe(map( (r: Response) => r.json()));
    }

    // VALORES
    // lubricantes
    get_lubricantes_valores(page?, valido_desde?, equipo?) {
      let myParams = new URLSearchParams();
      myParams.set('page', page || 1);
      myParams.set('valido_desde', valido_desde || '');
      myParams.set('equipo', equipo || '');
      return this.http.get('/api/taller/valores/lubricantes/', myParams).pipe(map((r: Response) => r.json()));
    }
    get_lubricante_valor(item: ILubricantesValores) {
      return this.http.get(`/api/taller/valores/lubricantes/${item.pk}/`).pipe(map((r: Response) => r.json()));
    }
    put_lubricante_valor(item: ILubricantesValores) {
      const bodyString = JSON.stringify(item);
      return this.http.put(`/api/taller/valores/lubricantes/${item.pk}/`, bodyString)
        .pipe(map((r: Response) => r.json()));
    }
    get_items_lubricantes() {
      return this.http.get('/api/taller/valores/items-lubricantes/').pipe(map((r: Response) => r.json()));
    }
    get_last_values_from_items_lubricantes() {
      return this.http.get('/api/taller/valores/items-lubricantes/latest/').pipe(map((r: Response) => r.json()));
    }
    create_new_values_lubricantes(periodo: IPeriodo, values: any) {
      const bodyString = JSON.stringify(values);
      return this.http.post(`/api/taller/valores/lubricantes/crear-nuevos/?periodo_id=${periodo.pk}`, bodyString)
        .pipe(map((r: Response) => r.json()));
    }

    // tren de rodaje
    get_tren_rodaje_valores(page?, valido_desde?, equipo?) {
      let myParams = new URLSearchParams();
      myParams.set('page', page || 1);
      myParams.set('valido_desde', valido_desde || '');
      myParams.set('equipo', equipo || '');
      return this.http.get('/api/taller/valores/tren_rodaje/', myParams).pipe(map((r: Response) => r.json()));
    }
    get_tren_rodaje_valor(item: ITrenRodajeValores) {
      return this.http.get(`/api/taller/valores/tren_rodaje/${item.pk}/`).pipe(map((r: Response) => r.json()));
    }
    put_tren_rodaje_valor(item: ITrenRodajeValores) {
      const bodyString = JSON.stringify(item);
      return this.http.put(`/api/taller/valores/tren_rodaje/${item.pk}/`, bodyString)
        .pipe(map((r: Response) => r.json()));
    }
    get_last_values_from_tren_rodaje() {
      return this.http.get('/api/taller/valores/tren_rodaje/latest/').pipe(map((r: Response) => r.json()));
    }
    create_new_values_tren_rodaje(periodo: IPeriodo, values: any) {
      const bodyString = JSON.stringify(values);
      return this.http.post(`/api/taller/valores/tren_rodaje/crear-nuevos/?periodo_id=${periodo.pk}`, bodyString)
        .pipe(map((r: Response) => r.json()));
    }

    // posesion
    get_posesion_valores(page?, valido_desde?, equipo?) {
      let myParams = new URLSearchParams();
      myParams.set('page', page || 1);
      myParams.set('valido_desde', valido_desde || '');
      myParams.set('equipo', equipo || '');
      return this.http.get('/api/taller/valores/posesion/', myParams).pipe(map((r: Response) => r.json()));
    }
    get_posesion_valor(item: IPosesionValores) {
      return this.http.get(`/api/taller/valores/posesion/${item.pk}/`).pipe(map((r: Response) => r.json()));
    }
    put_posesion_valor(item: IPosesionValores) {
      const bodyString = JSON.stringify(item);
      return this.http.put(`/api/taller/valores/posesion/${item.pk}/`, bodyString)
        .pipe(map((r: Response) => r.json()));
    }
    get_last_values_from_posesion() {
      return this.http.get('/api/taller/valores/posesion/latest/').pipe(map((r: Response) => r.json()));
    }
    create_new_values_posesion(periodo: IPeriodo, values: any) {
      const bodyString = JSON.stringify(values);
      return this.http.post(`/api/taller/valores/posesion/crear-nuevos/?periodo_id=${periodo.pk}`, bodyString)
        .pipe(map((r: Response) => r.json()));
    }

    // reparaciones
    get_reparaciones_valores(page?, valido_desde?, equipo?) {
      let myParams = new URLSearchParams();
      myParams.set('page', page || 1);
      myParams.set('valido_desde', valido_desde || '');
      myParams.set('equipo', equipo || '');
      return this.http.get('/api/taller/valores/reparaciones/', myParams).pipe(map((r: Response) => r.json()));
    }
    get_reparaciones_valor(item: IReparacionesValores) {
      return this.http.get(`/api/taller/valores/reparaciones/${item.pk}/`).pipe(map((r: Response) => r.json()));
    }
    put_reparaciones_valor(item: IReparacionesValores) {
      const bodyString = JSON.stringify(item);
      return this.http.put(`/api/taller/valores/reparaciones/${item.pk}/`, bodyString)
        .pipe(map((r: Response) => r.json()));
    }
    get_reparaciones_valores_vigente() {
      return this.http.get(`/api/taller/valores/reparaciones/latest/`).pipe(map((r: Response) => r.json()));
    }

    create_new_values_reparaciones(periodo: IPeriodo) {
      const bodyString = JSON.stringify({periodo_pk: periodo.pk});
      return this.http.post(`/api/taller/valores/reparaciones/crear-nuevos/`, bodyString)
        .pipe(map((r: Response) => r.json()));
    }


    // mano_obra
    get_mano_obra_valores(page?, valido_desde?) {
      let myParams = new URLSearchParams();
      myParams.set('page', page || 1);
      myParams.set('valido_desde', valido_desde || '');
      return this.http.get('/api/taller/valores/mano_obra/', myParams).pipe(map((r: Response) => r.json()));
    }
    get_mano_obra_valor(item: IManoObraValores) {
      return this.http.get(`/api/taller/valores/mano_obra/${item.pk}/`).pipe(map((r: Response) => r.json()));
    }
    put_mano_obra_valor(item: IManoObraValores) {
      const bodyString = JSON.stringify(item);
      return this.http.put(`/api/taller/valores/mano_obra/${item.pk}/`, bodyString)
        .pipe(map((r: Response) => r.json()));
    }

    post_mano_obra_valor(item: IManoObraValores) {
      const bodyString = JSON.stringify(item);
      return this.http.post(`/api/taller/valores/mano_obra/`, bodyString)
        .pipe(map((r: Response) => r.json()));
    }

    // alquilados
    get_alquilados_valores(page?, valido_desde?, equipo?) {
      let myParams = new URLSearchParams();
      myParams.set('page', page || 1);
      myParams.set('valido_desde', valido_desde || '');
      myParams.set('equipo', equipo || '');
      return this.http.get('/api/taller/valores/alquilados/', myParams).pipe(map((r: Response) => r.json()));
    }
    get_alquilados_valor(item: IEquipoAlquiladoValores) {
      return this.http.get(`/api/taller/valores/alquilados/${item.pk}/`).pipe(map((r: Response) => r.json()));
    }
    put_alquilados_valor(item: IEquipoAlquiladoValores) {
      const bodyString = JSON.stringify(item);
      return this.http.put(`/api/taller/valores/alquilados/${item.pk}/`, bodyString)
        .pipe(map((r: Response) => r.json()));
    }

    get_last_values_from_alquilados() {
      return this.http.get('/api/taller/valores/alquilados/latest/').pipe(map((r: Response) => r.json()));
    }
    create_new_values_alquilados(periodo: IPeriodo, values: any) {
      const bodyString = JSON.stringify(values);
      return this.http.post(`/api/taller/valores/alquilados/crear-nuevos/?periodo_id=${periodo.pk}`, bodyString)
        .pipe(map((r: Response) => r.json()));
    }

    // markup
    get_markup_valores(page?, valido_desde?, equipo?) {
      let myParams = new URLSearchParams();
      myParams.set('page', page || 1);
      myParams.set('valido_desde', valido_desde || '');
      myParams.set('equipo', equipo || '');
      return this.http.get('/api/taller/valores/markup/', myParams).pipe(map((r: Response) => r.json()));
    }
    get_markup_valor(item: IEquipoMarkupValores) {
      return this.http.get(`/api/taller/valores/markup/${item.pk}/`).pipe(map((r: Response) => r.json()));
    }
    put_markup_valor(item: IEquipoMarkupValores) {
      const bodyString = JSON.stringify(item);
      return this.http.put(`/api/taller/valores/markup/${item.pk}/`, bodyString)
        .pipe(map((r: Response) => r.json()));
    }

    get_last_values_from_markup() {
      return this.http.get('/api/taller/valores/markup/latest/').pipe(map((r: Response) => r.json()));
    }
    create_new_values_markup(periodo: IPeriodo, values: any) {
      const bodyString = JSON.stringify(values);
      return this.http.post(`/api/taller/valores/markup/crear-nuevos/?periodo_id=${periodo.pk}`, bodyString)
        .pipe(map((r: Response) => r.json()));
    }
  }

