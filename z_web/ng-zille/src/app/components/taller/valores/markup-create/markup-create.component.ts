import { Component, OnInit } from '@angular/core';
import { Periodo } from './../../../../models/Periodo';
import { CoreService } from './../../../../services/core/core.service';
import { Router } from '@angular/router';
import { TallerService } from './../../../../services/taller.service';
import { ModalService } from './../../../../services/core/modal.service';
import { NotificationService } from './../../../../services/core/notifications.service';
import { EquipoMarkupValores } from './../../../../models/EquipoMarkupValores';
import {
  IEquipoMarkupValores,
  IParametrosGenerales
  } from './../../../../models/Interfaces';

import * as moment from 'moment';
import { valid } from 'semver';


@Component({
  selector: 'app-markup-create',
  templateUrl: './markup-create.component.html',
  styles: []
})
export class MarkupCreateComponent implements OnInit {

  sel_periodo: Periodo;
  current_periodo_id: number;
  periodos: Periodo[] = [];

  current_gral_parametro: IParametrosGenerales;
  gral_parametros: IParametrosGenerales[] = [];

  valores: Array<IEquipoMarkupValores> = [];
  nuevos_valores: Array<EquipoMarkupValores> = [];

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

    this.tallerServ.get_last_values_from_markup().subscribe(
      valores => {
        this.nuevos_valores = new Array<EquipoMarkupValores>();
        if (valores != {}) {
          this.valores = valores['latest'] as Array<IEquipoMarkupValores>;
          this.current_gral_parametro = valores['parametros'];
          this.current_periodo_id = this.current_gral_parametro.valido_desde_id;
        } else {
          this.valores = new Array<IEquipoMarkupValores>();
        }

        this.tallerServ.get_equipos_propios_activos_list().subscribe(
          equipos => {
            equipos['equipos'].forEach((val, idx) => {
              const valor = this.valores.find(a => a.equipo_id == val.id);
              if (valor) {
                delete valor.pk;
                this.nuevos_valores.push(valor);
              } else {
                this.nuevos_valores.push({
                  equipo: val,
                  equipo_id: val.id,
                  markup: 0,
                  costo_mensual_del_activo_calculado: 0,
                  costo_mensual_del_activo_con_mo_calculado: 0,
                  costo_equipo_calculado: 0,
                  costo_mensual_mo_logistico: 0
                } as EquipoMarkupValores);
              }

            });
          },
          err => console.error(err),
          () => this.is_loading = false
        );
      },
      err => console.error(err)
    );
  }

  trackByIndex(index: number, item: IEquipoMarkupValores) {
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
      'Crear nuevos valores de markup',
      () => this.crearNuevosValores()
    ).open();
  }


  crearNuevosValores() {

    const valores = this.nuevos_valores.map(item => {
      return {equipo_id: item.equipo_id, markup: item.markup}
    });
    this.tallerServ.create_new_values_markup(this.sel_periodo, valores).subscribe(
      data => {
        if (data.status === 'ok') {
          this.notificationServ.success('Exito: ' + data.message);
          this.router.navigate(['/taller/valores', {
            outlets: {
              'details': null,
              'tabs': 'markup'
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

  verifyPercentage(idx: number) {
    console.log(this.nuevos_valores[idx].markup);
    if (this.nuevos_valores[idx].markup < 0) {
      this.nuevos_valores[idx].markup = 0;
    }
  }
}
