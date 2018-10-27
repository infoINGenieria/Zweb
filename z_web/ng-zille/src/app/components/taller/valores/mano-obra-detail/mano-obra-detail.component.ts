import { NotificationService } from './../../../../services/core/notifications.service';
import { IManoObraValores } from './../../../../models/Interfaces';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { TallerService } from '../../../../services/taller.service';
import { ModalService } from '../../../../services/core/modal.service';

@Component({
  selector: 'app-mano-obra-detail',
  templateUrl: './mano-obra-detail.component.html',
})
export class ManoObraDetailComponent implements OnInit {

  item: IManoObraValores;
  editing = false;

  is_saving = false;

  constructor(
    private route: ActivatedRoute,
    public tallerServ: TallerService,
    public modal: ModalService,
    private notification: NotificationService
  ) { }

  ngOnInit() {
    this.route.params.subscribe(
      param => {
        this.item = Object.assign({}, this.tallerServ.tempStorage);  // hago una copia

      }
    );
  }

  to_edit(val = true) {
    this.editing = val;
  }

  guardarValorModal() {
    this.modal.setUp(
        '¿Desea guardar los valores de mano de obra?',
        'Guardado',
      () => this.guardarValor()
    ).open();
  }

  guardarValor() {
    this.is_saving = true;
    this.to_edit(false);
    this.tallerServ.put_mano_obra_valor(this.item).subscribe(
      item => {
        this.is_saving = false;
        this.item = item;
        this.notification.success('Item actualizado correctamente.');
        this.tallerServ.refreshListSubject.next();  // notificar que debe recargar
      },
      err => {
        console.log(err);
        this.notification.error("Occurrió un error al guardar. Intente nuevamente.")
        this.reset();
      },
    );

  }

  reset() {
    this.tallerServ.get_mano_obra_valor(this.item).subscribe(
      item => this.item = item
    );
    this.to_edit(false);
  }
}
