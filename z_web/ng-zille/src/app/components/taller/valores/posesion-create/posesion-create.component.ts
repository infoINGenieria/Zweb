import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { Periodo } from './../../../../models/Periodo';
import { PosesionValores } from './../../../../models/PosesionValores';
import { CoreService } from './../../../../services/core/core.service';
import { TallerService } from './../../../../services/taller.service';
import { ModalService } from './../../../../services/core/modal.service';
import { NotificationService } from './../../../../services/core/notifications.service';

import { IPosesionValores, IParametrosGenerales, IPeriodo } from './../../../../models/Interfaces';

import * as moment from 'moment';


@Component({
  selector: 'app-posesion-create',
  templateUrl: './posesion-create.component.html',
  styleUrls: ['./posesion-create.component.scss']
})
export class PosesionCreateComponent implements OnInit {

  sel_periodo: Periodo;
  current_periodo_id: number;
  periodos: Periodo[] = [];
  is_loading = true;

  valores: Array<IPosesionValores> = [];
  nuevos_valores: Array<PosesionValores> = [];
  current_gral_parametro: IParametrosGenerales;
  gral_parametros: IParametrosGenerales[] = [];

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
      param => this.gral_parametros = param['results'] as Array<IParametrosGenerales>
    );

    this.tallerServ.get_last_values_from_posesion().subscribe(
      data => {
        this.valores = data['latest'] as IPosesionValores[];
        this.valores.forEach((val, idx) => {
          const new_v = Object.assign(new PosesionValores, val);
          this.nuevos_valores.push(new_v);
        });
        console.log(this.nuevos_valores);
        this.current_gral_parametro = data['parametros'];
        this.current_periodo_id = this.current_gral_parametro.valido_desde_id;
        this.is_loading = false;
      },
      err => console.log(err),
      () => this.is_loading = false
    );
  }

  trackByIndex(index: number, item: IPosesionValores) {
    return index;
  }

  get get_periodos_disponibles(): Periodo[] {
    try {
      const currentPeriodo = this.periodos.find(a => a.pk === this.current_periodo_id) as Periodo;
      const limit = moment(currentPeriodo.fecha_inicio, 'DD/MM/YYYY');
      return this.periodos.filter(a => limit.isBefore(moment(a.fecha_inicio, 'DD/MM/YYYY')));
    } catch (ex) {
      return [];
    }
  }

  get currentPeriodo() {
    return this.periodos.find(a => a.pk === this.current_periodo_id);
  }

  getParam(periodo: Periodo) {
    return this.gral_parametros.find(a => a.valido_desde_id === periodo.pk);
  }

  get targetDolar(): number {
    let dolar = 0;
    try {
      if (!this.sel_periodo) {
        return this.currentDolar;
      }
      dolar = this.getParam(this.sel_periodo).valor_dolar;
      return Number(dolar);
    } catch (ex) {
      return 0;
    }
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

  getTotal(idx: number) {
    try {
      const item: PosesionValores = this.nuevos_valores[idx] as PosesionValores;
      return item.costo_anual(this.targetDolar);
    } catch (ex) {
      console.log(ex);
    }
  }

  crearNuevosValoresModal() {
    this.modal.setUp(
      'Esta operación puede demorar unos segundos. ¿Continuar?',
      'Crear nuevos valores de posesión',
    () => this.crearNuevosValores()
  ).open();
  }


  crearNuevosValores() {
    this.tallerServ.create_new_values_posesion(this.sel_periodo, this.nuevos_valores).subscribe(
      data => {
        if (data.status === 'ok') {
          this.notificationServ.success('Exito: ' + data.message);
          this.router.navigate(['/taller/valores', {
            outlets: {
              'details': null,
              'tabs': 'posesion'
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
