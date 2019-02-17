import { Component, OnInit } from '@angular/core';
import { Periodo } from './../../../../models/Periodo';
import { CoreService } from './../../../../services/core/core.service';
import { Router } from '@angular/router';
import { TallerService } from './../../../../services/taller.service';
import { ModalService } from './../../../../services/core/modal.service';
import { NotificationService } from './../../../../services/core/notifications.service';
import {
  IParametrosGenerales,
  IEquipoAlquiladoValores
  } from './../../../../models/Interfaces';

import * as moment from 'moment';

@Component({
  selector: 'app-alquilados-create',
  templateUrl: './alquilados-create.component.html',
  styles: []
})
export class AlquiladosCreateComponent implements OnInit {

  sel_periodo: Periodo;
  current_periodo_id: number;
  periodos: Periodo[] = [];

  current_gral_parametro: IParametrosGenerales;
  gral_parametros: IParametrosGenerales[] = [];

  valores: Array<IEquipoAlquiladoValores> = [];
  nuevos_valores: Array<IEquipoAlquiladoValores> = [];

  is_loading = true;

  constructor(
    public coreServ: CoreService,
    public router: Router,
    public tallerServ: TallerService,
    public modal: ModalService,
    public notificationServ: NotificationService
  ) { }

  ngOnInit() {
    this.coreServ.get_periodos_list().subscribe(
      periodo => this.periodos = periodo as Periodo[],
      err => console.error(err)
    );

    this.tallerServ.get_parametros_generales_list().subscribe(
      param => this.gral_parametros = param['results'] as Array<IParametrosGenerales>
    );

    this.tallerServ.get_last_values_from_alquilados().subscribe(
      valores => {
        this.nuevos_valores = [];
        if (valores != {}) {
          this.valores = valores['latest'] as Array<IEquipoAlquiladoValores>;
          this.current_gral_parametro = valores['parametros'];
          this.current_periodo_id = this.current_gral_parametro.valido_desde_id;
        } else {
          this.valores = new Array<IEquipoAlquiladoValores>();
        }

        this.tallerServ.get_equipos_alquilados_activos_list().subscribe(
          equipos => {
            equipos['equipos'].forEach((val, idx) => {
              const valor = this.valores.find(a => a.equipo_id == val.id);
              this.nuevos_valores.push({
                equipo: val,
                equipo_id: val.id,
                alquiler: valor ? valor.alquiler : 0,
                comentarios: ''
              } as IEquipoAlquiladoValores);
            });
          },
          err => console.error(err),
          () => this.is_loading = false
        );
      },
      err => console.error(err)
    );
  }

  trackByIndex(index: number, item: IEquipoAlquiladoValores) {
    return index;
  }

  get get_periodos_disponibles(): Periodo[] {
    try {
      const currentPeriodo = this.periodos.find(a => a.pk === this.current_periodo_id) as Periodo;
      const limit = moment(currentPeriodo.fecha_inicio, 'DD/MM/YYYY');
      return this.periodos.filter(a => limit.isBefore(moment(a.fecha_inicio, 'DD/MM/YYYY')));
    } catch (ex) {
      return this.periodos;
    }
  }

  get currentPeriodo() {
    return this.periodos.find(a => a.pk === this.current_periodo_id);
  }

  getParam(periodo: Periodo) {
    return this.gral_parametros.find(a => a.valido_desde_id === periodo.pk);
  }

  get currentDolar(): number {
    let dolar = 0;
    try {
      dolar = this.getParam(this.currentPeriodo).valor_dolar;
      return Number(dolar);
    } catch (ex) {
      return 0;
    }
  }

  get targetDolar(): number {
    let dolar = 0;
    try {
      console.log(this.getParam(this.sel_periodo));
      dolar = this.getParam(this.sel_periodo).valor_dolar;
      return Number(dolar);
    } catch (ex) {
      return 0;
    }
  }

  crearNuevosValoresModal() {
    this.modal.setUp(
      'Esta operación puede demorar unos segundos. ¿Continuar?',
      'Crear nuevos valores de tren de rodaje',
      () => this.crearNuevosValores()
    ).open();
  }


  crearNuevosValores() {

    this.tallerServ.create_new_values_alquilados(this.sel_periodo, this.nuevos_valores).subscribe(
      data => {
        if (data.status === 'ok') {
          this.notificationServ.success('Exito: ' + data.message);
          this.router.navigate(['/taller/valores', {
            outlets: {
              'details': null,
              'tabs': 'alquilados'
            }
          }]);
        } else {
          this.notificationServ.error('Error: ' + data.message);
        }
      },
      err => {
        console.error(err);
        this.notificationServ.error('Error en la comunicación. Intento nuevamente');
      }
    );
  }
}
