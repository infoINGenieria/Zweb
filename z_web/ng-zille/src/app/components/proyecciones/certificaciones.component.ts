import { Periodo } from './../../models/Periodo';
import { NotificationService } from './../../services/core/notifications.service';
import { Certificacion } from './../../models/Certificacion';
import { MyCurrencyFormatterDirective } from './../../directives/currency-formatter.directive';
import {
  IProyeccionCertificacion, ICentroCosto, IPeriodo,
  IItemProyeccionCertificacion } from './../../models/Interfaces';
import { RegistroService } from './../../services/registro/registro.service';
import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute} from '@angular/router';
import { CoreService } from '../../services/core/core.service';
import { fadeInAnimation } from '../../_animations/index';
import { Modal } from 'ngx-modialog/plugins/bootstrap';
import { ProyeccionesService } from '../../services/proyecciones.service';

@Component({
  selector: 'app-certificaciones',
  templateUrl: './certificaciones.component.html',
  styleUrls: ['./certificaciones.component.css'],
  animations: [fadeInAnimation],
})
export class CertificacionesComponent implements OnInit {

  constructor(
    private route: ActivatedRoute,
    private registro_service: RegistroService,
    private core_service: CoreService,
    private proyecciones_service: ProyeccionesService,
    private _notifications: NotificationService,
    private modal: Modal,
    private router: Router,
  ) { }

  centro_costo: ICentroCosto;
  periodos: IPeriodo[];

  revisiones: IProyeccionCertificacion[] = [];
  revision_actual: IProyeccionCertificacion = null;

  isDisabled = false;

  initialLoading = true;
  loadingProgress = 0;

  set_progress() {
    if (this.initialLoading) {
      this.loadingProgress += 1;
      if (this.loadingProgress > 2) {
        setTimeout(() => this.initialLoading = false, 500);
      }
    }
  }

  ngOnInit() {
    this.route.params.subscribe(val => {
      const obra_id = val['obra_id'];
      const rev = val['rev'] || null;
      this.core_service.get_centro_costos(obra_id).subscribe(cc => {
        this.centro_costo = cc;
        this.set_progress();
        this.refresh(obra_id, rev);
      });
      this.core_service.get_periodos_list().subscribe(periodos => {
        this.periodos = [];
        periodos.map(p => this.periodos.push(new Periodo(p)));
        this.set_progress();
      });
    });
  }

  refresh(obra_id?, rev?) {
    obra_id = obra_id || this.centro_costo.id;
    this.proyecciones_service
      .get_proyeccion_certificacion_list(obra_id)
      .subscribe(revisiones => {
        revisiones.map(revision => {
          revision.items.map(item => {
            item.monto = Number.parseFloat(String(item.monto));
          });
        });
        this.revisiones = revisiones;
        if (rev) {
          this.revision_actual = revisiones.find((i) => i.pk == rev);
          if (this.revision_actual) {
            this.set_progress();
            return;
          }
        }

        if (revisiones.length > 0) {
          this.revision_actual = revisiones[revisiones.length - 1];
        } else {
          this.revision_actual = new Object as IProyeccionCertificacion;
          this.revision_actual.items = [];
          this.revision_actual.periodo = this.periodos[this.periodos.length - 1];
          this.revision_actual.periodo_id = this.revision_actual.periodo.pk;
          this.revision_actual.centro_costo_id = this.centro_costo.id;
        }
        this.set_progress();
      });
      this.isDisabled = false;
  }

  trackByIndex(index: number, item: IItemProyeccionCertificacion) {
    return index;
  }

  itemIsValid(item: IItemProyeccionCertificacion): boolean {
    if (item.periodo) {
      if (item.monto == null || isNaN(Number.parseInt(item.monto + '')) || isNaN(item.monto)) {
        return false;
      }
      return true;
    }
    return false;
  }

  isAllValid() {
    let periodos = [];
    for (const av of this.revision_actual.items) {
      const id = this._tonum(av.periodo);
      if (periodos.indexOf(id) !== -1) {
        return false;
      }
      periodos.push(id);
    }
    return true;
  }

  find_real(item: IItemProyeccionCertificacion) {
    if (this.revision_actual && this.revision_actual.certificacion_real) {
      return this.revision_actual.certificacion_real.find((i) => {
        return i.periodo_id === item.periodo;
      });
    }
  }

  find_periodo(periodo_id: Number): Periodo {
    let periodo = this.periodos.find(i => i.pk == periodo_id);
    return periodo;
  }

  actualizarPeriodo() {
    if (this.revision_actual) {
      this.revision_actual.periodo = this.find_periodo(this.revision_actual.periodo_id);
    }
  }

  acumulado(item: IItemProyeccionCertificacion): number {
    const posicion = this.revision_actual.items.indexOf(item);
    let acumulado = 0.0;
    for (const av of this.revision_actual.items.slice(0, posicion + 1)) {
      acumulado += this._tonum(av.monto);
    }
    return acumulado;
  }


  acumuladoConsolidado(item: IItemProyeccionCertificacion): number {
    /*
      Suma acumulado de los datos reales y, cuando estos no existan,
      la proyección del mes correspondiente.
    */
    const posicion = this.revision_actual.items.indexOf(item);
    let acumulado = 0.0;
    for (const _item of this.revision_actual.items.slice(0, posicion + 1)) {
      let real = this.find_real(_item);
      if (real) {
        acumulado += this._tonum(real.total);
      } else {
        acumulado += this._tonum(_item.monto);
      }
    }
    return acumulado;
  }

  aniadirCertificacion() {
    let item = new Object as IItemProyeccionCertificacion;
    this.revision_actual.items.push(item);
  }

  validate(): boolean {
    for (let item of this.revision_actual.items) {
      if (!this.itemIsValid(item)) {
        this._notifications.error('Corrija primero los ítems con fondo rojo.');
        return false;
      }
    }
    if ( !this.isAllValid()) {
      this._notifications.error('Hay más de un ítem con el mismo periodo seleccionado.');
      return false;
    }
    return true;
  }

  guardarActualModal() {
    if (!this.validate()) {
      return;
    }
    if (this.revision_actual.es_base) {
      const msg = `Está a punto de guardar los cambios en la línea BASE ` +
                  `${this.revision_actual.base_numero}</b>. ¿Continuar?`;
      const dialogRef = this.modal.confirm()
      .showClose(true)
      .title('Guardar línea base')
      .message(msg)
      .cancelBtn('Cancelar')
      .okBtn('Si, continuar!')
      .open();
      dialogRef.then(
        dialog => {
          dialog.result.then(
            result => this.guardarActual(),
            () => {}
          );
        },
      );
    } else {
      this.guardarActual();
    }
  }


  guardarActual() {
    if (!this.validate()) {
      return;
    }
    this.isDisabled = true;

    if (this.revision_actual.pk) {
      this.proyecciones_service.update_certificacion_proyeccion(this.revision_actual).subscribe(
        avance => {
          this._notifications.success('Se guardó correctamente la proyección.');
          this.refresh(this.centro_costo.id, avance.pk);
        },
        error => this.handleError(error),
        () => this.isDisabled = false
      );
    } else {
      this.proyecciones_service.create_certificacion_proyeccion(this.revision_actual).subscribe(
        avance => {
          this._notifications.success('Se creó correctamente la proyección.');
          this.refresh(this.centro_costo.id, avance.pk);
        },
        error => this.handleError(error),
        () => this.isDisabled = false
      );
    }
  }

  create_new_version_modal() {
    if (!this.validate()) {
      return;
    }
    const periodo = this.find_periodo(this.revision_actual.periodo_id);
    const msg = `Está a punto de crear una nueva revisión de la proyección ` +
                `para el periodo de <b>${periodo.descripcion}</b>. ¿Continuar?`;
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Guardar como nueva revisión')
    .message(msg)
    .cancelBtn('Cancelar')
    .okBtn('Si, crear!')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => this.crearRevision(),
          () => {}
        );
      },
    );
  }

  crearRevision() {
    this.isDisabled = true;
    let new_revision: IProyeccionCertificacion = Object.assign({}, this.revision_actual);
    new_revision.es_base = false;
    new_revision.base_numero = null;
    new_revision.pk = null;
    new_revision.items = this.revision_actual.items.map(
      item => {
        let new_item = new Object as IItemProyeccionCertificacion;
        new_item.monto = item.monto;
        new_item.periodo = item.periodo;
        return new_item;
      }
    );
    this.proyecciones_service.create_certificacion_proyeccion(new_revision).subscribe(
      revision => {
        this._notifications.success('Se creó una nueva revisión de la proyección');
        this.router.navigate(['/proyecciones', this.centro_costo.id, 'certificaciones', revision.pk]);
      },
      error => this.handleError(error)
    );
  }

  eliminarItemProyeccion(obj: IItemProyeccionCertificacion) {
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Quitar ítem')
    .message(
      '¿Está seguro que desea <b>quitar</b> este ítem de la proyección ' +
      'de certificacion del sistema?<br><b>Esta acción se confirmará al guardar.</b>')
    .cancelBtn('Cancelar')
    .okBtn('Quitar')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => {
            const idx = this.revision_actual.items.indexOf(obj);
            this.revision_actual.items.splice(idx, 1);
          },
          () => {}
        );
      },
    );
  }

  establecerComoBaseModal() {
    if (!this.validate()) {
      return;
    }
    if (this.revision_actual.es_base) {
      this._notifications.error('Esta revisión ya es BASE.');
      return;
    }
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Establecer nueva línea BASE')
    .message(`¿Está seguro que desea establecer una <b>nueva línea BASE</b> a partir de esta revisión?`)
    .cancelBtn('Cancelar')
    .okBtn('Si, establecer!')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => this.establecerComoBase(),
          () => {}
        );
      },
    );
  }

  establecerComoBase() {
    this.isDisabled = true;
    let new_revision: IProyeccionCertificacion = Object.assign({}, this.revision_actual);
    new_revision.es_base = true;
    new_revision.base_numero = this.revision_actual.base_vigente + 1;
    new_revision.pk = null;
    new_revision.items = this.revision_actual.items.map(
      item => {
        let new_item = new Object as IItemProyeccionCertificacion;
        new_item.monto = item.monto;
        new_item.periodo = item.periodo;
        return new_item;
      }
    );
    this.proyecciones_service.create_certificacion_proyeccion(new_revision).subscribe(
      revision => {
        this._notifications.success(`Se creó la nueva revisión BASE ${revision.base_numero}`);
        this.router.navigate(['/proyecciones', this.centro_costo.id, 'certificaciones', revision.pk]);
      },
      error => this.handleError(error)
    );
  }

  deleteRevisionActual() {
    if (this.revision_actual.es_base) {
      this._notifications.error('No puede quitarse una revisión BASE.');
      return;
    }
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Confirmación de eliminación')
    .message(`¿Está seguro que desea <b>eliminar</b> esta revisión del sistema?` +
             `<br><b>Esta acción no puede deshacerse.</b>`)
    .cancelBtn('Cancelar')
    .okBtn('Eliminar')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => {
            this.isDisabled = true;
            this.proyecciones_service.delete_proyeccion_certificacion(this.revision_actual).subscribe(
              r => {
                this.refresh();
                this._notifications.success('Revisión eliminada correctamente.');
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
    if (error.status === 400) {
      let error_json = JSON.parse(error._body);
      this._notifications.error(error_json.join());
    } else {
      this._notifications.error('Un error ha ocurrido. Por favor, intente nuevamente.');
    }
    this.isDisabled = false;
  }
}
