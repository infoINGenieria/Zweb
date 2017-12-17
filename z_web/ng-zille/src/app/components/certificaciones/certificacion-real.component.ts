import { Modal } from 'ngx-modialog/plugins/bootstrap';
import { fadeInAnimation } from './../../_animations/fade-in.animation';
import { itemAnim } from './../../_animations/itemAnim';
import { NotificationService } from './../../services/core/notifications.service';
import { CoreService } from './../../services/core/core.service';
import { ICertificacion, IPeriodo, ICentroCosto, ICertificacionItem } from './../../models/Interfaces';
import { RegistroService } from './../../services/registro/registro.service';
import { ActivatedRoute, Router } from '@angular/router';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-certificacion-real',
  templateUrl: './certificacion-real.component.html',
  animations: [fadeInAnimation, itemAnim]
})
export class CertificacionRealComponent implements OnInit {

  loading = 0;

  certificacion: ICertificacion;

  centro_costos: ICentroCosto[] = [];
  periodos: IPeriodo[] = [];

  CONCEPTOS: any = [
    {'key': 'basica', 'text': 'Certificación Básica'},
    {'key': 'cambios', 'text': 'Órdenes de cambio'},
    {'key': 'reajuste', 'text': 'Reajuste de precios'},
    {'key': 'reclamos', 'text': 'Reclamos reconocidos'},
  ];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private registroServ: RegistroService,
    private core_service: CoreService,
    private _notifications: NotificationService,
    private modal: Modal
  ) {
    // create empty objects
    this.certificacion = new Object as ICertificacion;
    this.certificacion.obra_id = null;
    this.certificacion.periodo_id = null;
    this.addItem();
    route.params.subscribe(val => {
      const pk = val['pk'];
      if (pk) {
        const version = val['version'];
        this.registroServ.get_certificacion_real(pk).subscribe(cert => {
          this.certificacion = cert as ICertificacion;
          this.certificacion.items = this.certificacion.items.map(item => item as ICertificacionItem);
        });
      }
      this.setInProgress();
    });
  }

  ngOnInit() {
    this.core_service.get_centro_costos_list().subscribe(centros => {
      this.centro_costos = centros;
      this.setInProgress();
    });
    this.core_service.get_periodos_list().subscribe(p => {
      this.periodos = p as IPeriodo[];
      this.setInProgress();
    }, error => this.handleError(error));
  }

  setInProgress() {
    setTimeout(() => {
      this.loading += 1;
    }, 50);

  }

  handleError(error: any) {
    this._notifications.error(error._body || error);
  }

  trackByIndex(index: number, item: ICertificacionItem) {
    return index;
  }

  itemIsValid(item: ICertificacionItem): boolean {
    if (item.concepto && this._tonum(item.monto) > 0) {
      return true;
    }
    return false;
  }

  checkAllItem(): boolean {
    if (this.certificacion.items !== undefined) {
      if (this.certificacion.items.length === 0) {
        return false;
      }
      for (const item of this.certificacion.items) {
        if (!this.itemIsValid(item)) {
          return false;
        }
      }
    }
    return true;
  }

  addItem() {
    const item = new Object as ICertificacionItem;
    item.monto = 0;
    item.concepto = 'basica';
    item.observaciones = '';
    if (this.certificacion.items === undefined) {
      this.certificacion.items = [];
    }
    this.certificacion.items.push(item);
  }

  removeItem(item: ICertificacionItem) {
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Confirmación de eliminación')
    .message(`¿Está seguro que desea remover este ítem del listado?`)
    .cancelBtn('Cancelar')
    .okBtn('Eliminar')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => {
            const index = this.certificacion.items.indexOf(item);
            this.certificacion.items.splice(index, 1);
          },
          () => {}
        );
      },
    );
  }

  get total_items() {
    let total = 0;
    if (this.certificacion.items !== undefined) {
      for (const item of this.certificacion.items) {
        total += this._tonum(item.monto);
      }
    }
    return total;
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


  create_certificacion_modal() {
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Crear certificacion')
    .message(`Está a punto de crear una nueva certificacion ¿Continuar?`)
    .cancelBtn('Cancelar')
    .okBtn('Si, crear!')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => this.create_certificacion(),
          () => {}
        );
      },
    );
  }

  create_certificacion() {
    this.registroServ.create_certificacion_real(this.certificacion).subscribe(certificacion => {
      this.certificacion = certificacion;
      this._notifications.success('Certificación guardado correctamente.');
      this.router.navigate(['/certificaciones', this.certificacion.pk]);
    }, error => this.handleError(error));
  }

  save_certificacion_modal() {
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Guardar certificación')
    .message(`¿Guardar la certificación actual?`)
    .cancelBtn('Cancelar')
    .okBtn('Si, guardar!')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => this.save_certificacion(),
          () => {}
        );
      },
    );
  }

  save_certificacion() {
    this.registroServ.update_certificacion_real(this.certificacion).subscribe(certificacion => {
      this.certificacion = certificacion;
      this._notifications.success(`Certificación actualizada correctamente.`);
    }, error => this.handleError(error));
  }
}
