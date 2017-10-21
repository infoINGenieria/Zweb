import { IDatePickerConfig } from 'ng2-date-picker';
import { CoreService } from './../../services/core/core.service';
import { Modal } from 'ngx-modialog/plugins/bootstrap';
import { NotificationService } from './../../services/core/notifications.service';
import { fadeInAnimation } from './../../_animations/fade-in.animation';
import { itemAnim } from './../../_animations/itemAnim';
import { slideInOutAnimation } from './../../_animations/slide-in-out.animation';
import { Component, OnInit, ViewChild } from '@angular/core';
import { NgForm } from '@angular/forms';

import { PresupuestosService } from './../../services/presupuestos/presupuestos.service';
import { IPresupuesto, ICentroCosto } from './../../models/Interfaces';

@Component({
  selector: 'app-presupuestos',
  templateUrl: './presupuestos.component.html',
  styleUrls: ['./presupuestos.component.css'],
  animations: [fadeInAnimation]
})
export class PresupuestosComponent implements OnInit {

  presupuestos: IPresupuesto[] = [];
  centro_costos: ICentroCosto[] = [];
  loaded = false;

  constructor(
    private presupuestos_service: PresupuestosService,
    private core_serv: CoreService,
    private _notifications: NotificationService,
    private _modal: Modal
  ) { }

  datePickerConfig: IDatePickerConfig = {
    'format': 'DD/MM/YYYY',
    'drops': 'down',
    'locale': 'es'
  };

  refresh() {
    this.loaded = false;
    this.presupuestos_service.get_presupuestos().subscribe(presupuestos => {
      this.presupuestos = presupuestos as IPresupuesto[];
      this.loaded = true;
    }, error => this.handleError(error));
  }
  ngOnInit() {
    this.refresh();
    this.core_serv.get_centro_costos_list().subscribe(cc => {
      this.centro_costos = cc as ICentroCosto[];
    }, error => this.handleError(error));
  }

  handleError(error: any) {
    this._notifications.error(error);
  }

  delete(presupuesto: IPresupuesto) {
    const dialogRef = this._modal.confirm()
    .showClose(true)
    .title('Confirmación de eliminación')
    .message(`¿Está seguro que desea <b>eliminar</b> este presupuesto del sistema?<br><b>Esta acción no puede deshacerse.</b>`)
    .cancelBtn('Cancelar')
    .okBtn('Eliminar')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => {
            this.presupuestos_service.delete_presupuesto(presupuesto).subscribe(
              r => {
                this.refresh();
                this._notifications.success('Presupuesto eliminado correctamente.');
              },
              error => this.handleError(error));
          },
          () => {}
        );
      },
    );
  }

  filterList(form: NgForm) {
    const { centro_costo, desde, hasta } = form.value;
    this.loaded = false;
    this.presupuestos_service.get_presupuestos(centro_costo, desde, hasta).subscribe(presupuestos => {
      this.presupuestos = presupuestos as IPresupuesto[];
      this.loaded = true;
    }, error => this.handleError(error));
  }
}
