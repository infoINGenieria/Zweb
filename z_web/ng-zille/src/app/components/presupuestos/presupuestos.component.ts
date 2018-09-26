import { IDatePickerConfig } from 'ng2-date-picker';
import { CoreService } from '../../services/core/core.service';
import { NotificationService } from '../../services/core/notifications.service';
import { fadeInAnimation } from '../../_animations/fade-in.animation';
import { Component, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';

import { PresupuestosService } from '../../services/presupuestos/presupuestos.service';
import { IPresupuesto, ICentroCosto } from '../../models/Interfaces';
import { ModalService } from '../../services/core/modal.service';

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

  selectedPresupuesto: IPresupuesto;

  constructor(
    private presupuestos_service: PresupuestosService,
    private core_serv: CoreService,
    private _notifications: NotificationService,
    public modal: ModalService
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
    console.error(error);
    this._notifications.error(error._body || error);
  }

  delete(presupuesto: IPresupuesto) {
    this.selectedPresupuesto = presupuesto;
    this.modal.setUp(
      '¿Está seguro que desea <b>eliminar</b> este presupuesto del sistema?<br><b>Esta acción no puede deshacerse.</b>',
      'Confirmación de eliminación',
      () => this.eliminarPresupuesto()
    ).open();

  }

  eliminarPresupuesto() {
    this.presupuestos_service.delete_presupuesto(this.selectedPresupuesto).subscribe(
      r => {
        this.refresh();
        this._notifications.success('Presupuesto eliminado correctamente.');
      },
      error => this.handleError(error)
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
