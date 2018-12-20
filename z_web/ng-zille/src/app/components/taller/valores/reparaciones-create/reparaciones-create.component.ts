import { Router } from '@angular/router';
import { NotificationService } from './../../../../services/core/notifications.service';
import { Component, OnInit } from '@angular/core';
import { Periodo } from './../../../../models/Periodo';
import { TallerService } from './../../../../services/taller.service';
import { CoreService } from './../../../../services/core/core.service';
import { ModalService } from './../../../../services/core/modal.service';
import { IReparacionesValores, IParametrosGenerales } from './../../../../models/Interfaces';

import * as moment from 'moment';

@Component({
  selector: 'app-reparaciones-create',
  templateUrl: './reparaciones-create.component.html',
  styles: []
})
export class ReparacionesCreateComponent implements OnInit {

  currentPeriodo: Periodo;
  sel_periodo: Periodo;
  periodos: Periodo[] = [];

  items: Array<IReparacionesValores> = [];
  parametros: Array<IParametrosGenerales> = [];

  constructor(
    public coreServ: CoreService,
    public router: Router,
    public tallerServ: TallerService,
    public modal: ModalService,
    public notificationServ: NotificationService
  ) { }

  ngOnInit() {
    this.coreServ.get_periodos_list().subscribe(
      periodo => this.periodos = periodo as Periodo[]
    );

    this.tallerServ.get_parametros_generales_list().subscribe(
      param => this.parametros = param['results'] as Array<IParametrosGenerales>
    );

    this.tallerServ.get_reparaciones_valores_vigente().subscribe(
      valores => {
        this.items = valores['latest'] as IReparacionesValores[];
        this.currentPeriodo = new Periodo(this.items[0].valido_desde);
        this.sel_periodo = this.get_periodos_disponibles.length > 0 ? this.get_periodos_disponibles[0] : null;
      }
    );
  }

  get get_periodos_disponibles(): Periodo[] {
    try {
      const limit = this.currentPeriodo.fecha_inicio_obj();
      return this.periodos.filter(a => limit.isBefore(moment(a.fecha_inicio, 'DD/MM/YYYY')));
    } catch (ex) {
      return [];
    }
  }

  getParam(periodo: Periodo) {
    return this.parametros.find(a => a.valido_desde_id === periodo.pk);
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

  get diff(): number {
    return ((this.targetDolar / this.currentDolar) - 1) * 100;
  }

  get diffStr(): string {
    const _diff = this.diff;
    if (_diff > 0) {
      return `+${_diff.toFixed(2)} %`;
    } else {
      return `${_diff.toFixed(2)} %`;
    }
  }

  crearNuevosValoresModal() {
    this.modal.setUp(
      '¿Continuar?',
      'Crear nuevos valores de reserva para reparaciones',
    () => this.crearNuevosValores()
  ).open();
  }


  crearNuevosValores() {
    this.tallerServ.create_new_values_reparaciones(this.sel_periodo).subscribe(
      data => {
        if (data.status === 'ok') {
          this.notificationServ.success('Exito: ' + data.message);
          this.router.navigate(['/taller/valores', {
            outlets: {
              'details': null,
              'tabs': 'reparaciones'
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
