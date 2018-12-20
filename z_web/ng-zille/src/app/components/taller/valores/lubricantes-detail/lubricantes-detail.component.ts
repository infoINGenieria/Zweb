import { NotificationService } from './../../../../services/core/notifications.service';
import { ModalService } from './../../../../services/core/modal.service';
import { ILubricantesValoresItem } from './../../../../models/Interfaces';
import { ActivatedRoute } from '@angular/router';
import { Component, OnInit } from '@angular/core';
import { ILubricantesValores } from '../../../../models/Interfaces';
import { TallerService } from '../../../../services/taller.service';

@Component({
  selector: 'app-lubricantes-detail',
  templateUrl: './lubricantes-detail.component.html',
  styles: [
    `
    `
  ]
})
export class LubricantesDetailComponent implements OnInit {

  item: ILubricantesValores;
  editing = false;
  is_saving = false;

  public constructor(
    private route: ActivatedRoute,
    public tallerServ: TallerService,
    public modal: ModalService,
    private notification: NotificationService
    ) {
  }

  ngOnInit() {
    this.route.params.subscribe(
      param => {
        this.item = Object.assign({}, this.tallerServ.tempStorage);  // hago una copia
      }
    );
  }

  trackByIndex(index: number, item: ILubricantesValoresItem) {
    return index;
  }

  to_edit(val = true) {
    this.editing = val;
  }

  get_costo_mesual_calculado(item: ILubricantesValoresItem) {
      return item.parametros.cambios_por_anio * item.parametros.volumen_por_cambio * item.valor_unitario / 12;
  }

  guardarValorModal() {
    this.modal.setUp(
        '¿Desea guardar los valores de lubricantes?',
        'Guardado',
      () => this.guardarValor()
    ).open();
  }

  guardarValor() {
    this.is_saving = true;
    this.to_edit(false);
    this.tallerServ.put_lubricante_valor(this.item).subscribe(
      item => {
        this.is_saving = false;
        this.item = item;
        this.notification.success('Item actualizado correctamente.');
        this.tallerServ.refreshListSubject.next();  // notificar que debe recargar
      },
      err => {
        console.log(err);
        this.notification.error('Occurrió un error al guardar. Intente nuevamente.')
        this.reset();
      }
    );
  }

  reset() {
    this.tallerServ.get_lubricante_valor(this.item).subscribe(
      item => this.item = item
    );
    this.to_edit(false);
  }
}
