import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute} from '@angular/router';

import { Modal } from 'ngx-modialog/plugins/bootstrap';

import { fadeInAnimation } from '../../_animations/index';

import { CoreService } from '../../services/core/core.service';
import { NotificationService } from '../../services/core/notifications.service';
import { AvanceObraService } from './../../services/avanceobra.service';

import { ICentroCosto, ICertificacion, IAvanceObra, IPeriodo } from './../../models/Interfaces';
import 'rxjs/add/operator/map';

@Component({
  selector: 'app-avance-obra',
  templateUrl: './avance-obra.component.html',
  styleUrls: ['./avance-obra.component.css'],
  animations: [fadeInAnimation],
})
export class AvanceObraComponent implements OnInit {

  constructor(
    private route: ActivatedRoute,
    private avanceobra_serv: AvanceObraService,
    private core_service: CoreService,
    private _notifications: NotificationService,
    private modal: Modal
  ) { }

  centro_costo: ICentroCosto;
  avances: IAvanceObra[] = [];
  real_avances: IAvanceObra[] = [];
  periodos: IPeriodo[];

  isDisabled = false;

  ngOnInit() {
    this.route.params.subscribe(val => {
      const obra_id = val['obra_id'];
      this.core_service.get_centro_costos(obra_id).subscribe(cc => this.centro_costo = cc);
      this.core_service.get_periodos_list().subscribe(periodos => this.periodos = periodos);
      this.refresh(obra_id);
    });
  }

  refresh(obra_id?) {
    obra_id = obra_id || this.centro_costo.id;
    this.avanceobra_serv
    .get_avance_obra_proyeccion_list(obra_id)
    .subscribe(avances => {
      this.avances = [];
      avances.map(item => {
        let avance = item;
        avance.avance = Number.parseFloat(String(avance.avance));
        this.avances.push(avance);
      })
    });
  this.avanceobra_serv
    .get_avance_obra_real_list(obra_id)
    .subscribe(avances => {
      this.real_avances = [];
      avances.map(item => {
        let avance = item;
        avance.avance = Number.parseFloat(String(avance.avance));
        this.real_avances.push(avance);
      });
    });
  }

  itemIsValid(item: IAvanceObra): boolean {
    if (item.periodo_id && item.avance) {
      return true;
    }
    return false;
  }

  isAllValid() {
    let periodos = [];
    for (const av of this.avances) {
      const id = this._tonum(av.periodo_id)
      if (periodos.indexOf(id) !== -1) {
        return false;
      }
      periodos.push(id);
    }
    return true;
  }

  find_real(item: IAvanceObra) {
    if (this.real_avances){
      return this.real_avances.find((i) => {
        return i.periodo_id === item.periodo_id;
      });
    }
  }

  acumulado(item: IAvanceObra): number {
    const posicion = this.avances.indexOf(item);
    let acumulado = 0.0;
    for (const av of this.avances.slice(0, posicion + 1)) {
      acumulado += this._tonum(av.avance);
    }
    return acumulado;
  }

  acumuladoConsolidado(item: IAvanceObra): number {
    /*
      Suma acumulado de los datos reales y, cuando estos no existan,
      la proyección del mes correspondiente.
    */
    const posicion = this.avances.indexOf(item);
    let acumulado = 0.0;
    for (const av of this.avances.slice(0, posicion + 1)) {
      let real = this.find_real(av);
      if (real) {
        acumulado += this._tonum(real.avance);
      } else {
        acumulado += this._tonum(av.avance);
      }
    }
    return acumulado;
  }

  aniadirAvanceObra() {
    let avanceobra = new Object as IAvanceObra;
    avanceobra.centro_costo_id = this.centro_costo.id;
    this.avances.push(avanceobra);
  }

  guardarTodos() {
    for (let avance of this.avances) {
      if (!this.itemIsValid(avance)) {
        this._notifications.error('Corrija primero los ítems con fondo rojo.');
        return;
      }
    }
    if ( !this.isAllValid()) {
      this._notifications.error('Hay más de un ítem con el mismo periodo seleccionado.');
      return;
    }
    this.isDisabled = true;
    for (let avance of this.avances) {
      if (avance.pk) {
        this.avanceobra_serv.update_avance_obra_proyeccion(avance).subscribe(
          _avance => {}, error => this.handleError(error));
      } else {
        this.avanceobra_serv.create_avance_obra_proyeccion(avance).subscribe(
          _avance => {}, error => this.handleError(error));
      }
    }
    setTimeout(() => {
      this.isDisabled = false;
      this._notifications.success('Se guardó correctamente la proyección.');
      this.refresh();
    }, 1000);
  }

  guardarAvanceObra(obj: IAvanceObra) {
    if (!this.itemIsValid(obj)) {
      this._notifications.error('Asegúrese que los campos están completos.');
      return;
    }
    if (obj.pk) {
      this.avanceobra_serv.update_avance_obra_proyeccion(obj)
        .subscribe(
          _avance => {
            this._notifications.success('Datos guardado correctamente.');
            this.refresh();
          },
          error => this.handleError(error));
    } else {
      this.avanceobra_serv.create_avance_obra_proyeccion(obj)
        .subscribe(
          _avance => {
            this._notifications.success('Datos guardado correctamente.');
            this.refresh();
          },
          error => this.handleError(error));
    }
  }

  eliminarAvanceObra(obj: IAvanceObra) {
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Confirmación de eliminación')
    .message(
      '¿Está seguro que desea <b>eliminar</b> este ítem de la proyección ' +
      'de avance de obra del sistema?<br><b>Esta acción no puede deshacerse.</b>')
    .cancelBtn('Cancelar')
    .okBtn('Eliminar')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => {
            this.avanceobra_serv.delete_avance_obra_proyeccion(obj).subscribe(
              r => {
                this.refresh();
                this._notifications.success('Ítem eliminado correctamente.');
              },
              error => this.handleError(error));
          },
          () => {}
        );
      },
    );
  }



  _tonum(val): number {
    if (typeof val === 'number') {
      return val;
    }
    const newVal = parseFloat(val);
    if (!isNaN(newVal)) {
      return newVal;
    }
    return 0;
  }

  handleError(error: any) {
    this._notifications.error(error.statusText || 'Un error ha ocurrido. Por favor, intente nuevamente.');
  }
}
