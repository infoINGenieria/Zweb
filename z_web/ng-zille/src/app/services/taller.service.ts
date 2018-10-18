
import {throwError as observableThrowError,  Observable } from 'rxjs';
import { IPeriodo, ILubricantesValores, ITrenRodajeValores, IPosesionValores, IReparacionesValores, IReparacionesParametros, IManoObraValores, IEquipoAlquiladoValores, IEquipoMarkupValores } from './../models/Interfaces';
import { IParametrosGenerales, IAsistencia } from '../models/Interfaces';
import { IEquipo } from '../models/Interfaces';
import { BaseApiService } from './base-api/base-api.service';
import { Injectable } from '@angular/core';
import { Response, URLSearchParams } from '@angular/http';
import { map } from 'rxjs/operators';


@Injectable()
export class TallerService {

  public tempStorage: any;

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
  get_equipos_list(page?, ninterno?, marca?, modelo?, tipo?, dominio?, anio?, estado?, excluir_costos_taller?) {
    let myParams = new URLSearchParams();
    myParams.set('page', page || 1);
    myParams.set('n_interno', ninterno || '');
    myParams.set('marca', marca || '');
    myParams.set('modelo', modelo || '');
    myParams.set('equipo', tipo || '');
    myParams.set('dominio', dominio || '');
    myParams.set('año', anio || '');
    myParams.set('estado', estado || '');
    myParams.set('excluir_costos_taller', excluir_costos_taller || '');
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
  }

