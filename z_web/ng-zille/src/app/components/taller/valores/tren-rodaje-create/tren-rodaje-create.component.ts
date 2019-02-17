import { Component, OnInit } from '@angular/core';
import { Periodo } from './../../../../models/Periodo';
import { CoreService } from './../../../../services/core/core.service';
import { Router } from '@angular/router';
import { TallerService } from './../../../../services/taller.service';
import { ModalService } from './../../../../services/core/modal.service';
import { NotificationService } from './../../../../services/core/notifications.service';
import { ILubricanteItem, ITrenRodajeValores, IParametrosGenerales } from './../../../../models/Interfaces';

import * as moment from 'moment';


// clase para enviar los nuevos valores
class NewValueTrenRodaje {
  equipo_id: number;
  precio_neumatico: number;

  constructor(equipo_id: number, precio_neumatico?: number) {
    this.equipo_id = equipo_id;
    this.precio_neumatico = precio_neumatico;
  }
}

@Component({
  selector: 'app-tren-rodaje-create',
  templateUrl: './tren-rodaje-create.component.html',
  styles: []
})
export class TrenRodajeCreateComponent implements OnInit {

  sel_periodo: Periodo;
  current_periodo_id: number;
  periodos: Periodo[] = [];

  valores: Array<ITrenRodajeValores> = [];
  nuevos_valores: Array<NewValueTrenRodaje> = [];

  current_gral_parametro: IParametrosGenerales;
  gral_parametros: IParametrosGenerales[] = [];

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

    this.tallerServ.get_last_values_from_tren_rodaje().subscribe(
      data => {
        this.valores = data['latest'] as ITrenRodajeValores[];
        this.valores.forEach((val, idx) => {
          this.nuevos_valores.push(new NewValueTrenRodaje(val.equipo_id, Number(val.precio_neumatico)));
        });
        this.current_gral_parametro = data['parametros'];
        this.current_periodo_id = this.current_gral_parametro.valido_desde_id;
      },
      err => console.error(err),
      () => this.is_loading = false
    );
  }

  trackByIndex(index: number, item: ITrenRodajeValores) {
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

  get con_neumaticos(): ITrenRodajeValores[] {
    return this.valores.filter(a => a.parametros.tiene_neumaticos);
  }

  get sin_neumaticos(): ITrenRodajeValores[] {
    return this.valores.filter(a => !a.parametros.tiene_neumaticos);
  }

  findValor(equipo_id: number): NewValueTrenRodaje {
    return this.nuevos_valores.find(a => a.equipo_id === equipo_id);
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

  get usdDiff(): number {
    return ((this.targetDolar / this.currentDolar) - 1) * 100;
  }

  get usdDiffStr(): string {
    const _diff = this.usdDiff;
    if (_diff > 0) {
      return `+${_diff.toFixed(2)} %`;
    } else {
      if (_diff === -100) {
        return '-';
      }
      return `${_diff.toFixed(2)} %`;
    }
  }

  diffPrecio(actual: number, nuevo: number) {
    const variacion = ((nuevo / actual) - 1) * 100;
    if (variacion > 0) {
      return `+${variacion.toFixed(2)} %`;
    } else {
      if (variacion === -100) {
        return '-';
      }
      return `${variacion.toFixed(2)} %`;
    }
  }

  nuevoCostoOruga(costo_actual: number) {
    return costo_actual * (1 + (this.usdDiff / 100));
  }

  crearNuevosValoresModal() {
    this.modal.setUp(
      '¿Continuar?',
      'Crear nuevos valores de tren de rodaje',
      () => this.crearNuevosValores()
    ).open();
  }


  crearNuevosValores() {

    this.tallerServ.create_new_values_tren_rodaje(this.sel_periodo, this.nuevos_valores).subscribe(
      data => {
        if (data.status === 'ok') {
          this.notificationServ.success('Exito: ' + data.message);
          this.router.navigate(['/taller/valores', {
            outlets: {
              'details': null,
              'tabs': 'tren_rodaje'
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
