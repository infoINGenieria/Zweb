import { NotificationService } from './../../services/core/notifications.service';
import { fadeInAnimation } from './../../_animations/fade-in.animation';
import { ActivatedRoute } from '@angular/router';
import { Component, OnInit, HostBinding } from '@angular/core';
import { Modal } from 'ngx-modialog/plugins/bootstrap';

import { ITipoItemPresupuesto } from './../../models/Interfaces';
import { PresupuestoComponent } from './../presupuesto/presupuesto.component';
import { PresupuestosService } from './../../services/presupuestos/presupuestos.service';

@Component({
  selector: 'app-tipo-item-presupuesto',
  templateUrl: './tipo-item-presupuesto.component.html',
  styleUrls: ['./tipo-item-presupuesto.component.css'],
  animations: [fadeInAnimation]
})
export class TipoItemPresupuestoComponent implements OnInit {

  tipos: ITipoItemPresupuesto[] = [];

  constructor(
    private _service: PresupuestosService,
    private _notifications: NotificationService,
    public modal: Modal,
    public activatedRoute: ActivatedRoute) {
  }

  ngOnInit() {
    this.refresh_tipos();
  }

  refresh_tipos() {
    this._service.get_tipo_items().subscribe(tipos => this.tipos = tipos);
  }

  handleError(error: any) {
    this._notifications.error(error);
  }

  eliminar(item: ITipoItemPresupuesto) {
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Confirmación de eliminación')
    .message(`¿Está seguro que desea eliminar el tipo ${item.nombre} del sistema ?`)
    .cancelBtn('Cancelar')
    .okBtn('Eliminar')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => {
            this._service.delete_tipo_item(item).subscribe(
              r => {
                this.refresh_tipos();
                this._notifications.success('Tipo de ítem eliminado correctamente.');
              },
              error => this.handleError(error));
          },
          () => {}
        );
      },
    );
  }

  editar(item: ITipoItemPresupuesto) {
    const dialogRef = this.modal.prompt()
    .showClose(true)
    .title(`Editando ${item.nombre}`)
    .defaultValue(item.nombre)
    .cancelBtn('Cancelar')
    .okBtn('Guardar')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => {
            item.nombre = result;
            this._service.update_tipo_item(item).subscribe(
              r => {
                this.refresh_tipos();
                this._notifications.success('Modificado correctamente.');
              },
              error => this.handleError(error));
          },
          () => {}
        );
      },
    );
  }

  crear() {
    const dialogRef = this.modal.prompt()
      .showClose(true)
      .title('Añadir nuevo tipo de ítem')
      .cancelBtn('Cancelar')
      .okBtn('Crear')
      .open();
      dialogRef.then(
        dialog => {
          dialog.result.then(
            result => {
              this._service.create_tipo_item(result).subscribe(
                r => {
                  this.refresh_tipos();
                  this._notifications.success('Tipo de ítem agregado correctamente.');
                },
                error => this.handleError(error));
            },
            () => {}
          );
        },
      );
  }

}
