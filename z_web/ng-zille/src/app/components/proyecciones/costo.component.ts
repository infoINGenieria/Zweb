import { Periodo } from '../../models/Periodo';
import { PresupuestosService } from '../../services/presupuestos/presupuestos.service';
import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute} from '@angular/router';

import { Modal } from 'ngx-modialog/plugins/bootstrap/src/ngx-modialog-bootstrap.ng-flat';
import { MyCurrencyFormatterDirective } from '../../directives/currency-formatter.directive';

import { fadeInAnimation } from '../../_animations';
import { NotificationService } from '../../services/core/notifications.service';
import { CoreService } from '../../services/core/core.service';
import { ProyeccionesService } from '../../services/proyecciones.service';
import { RegistroService } from '../../services/registro/registro.service';

import {
  IProyeccionCosto, ICentroCosto, IPeriodo, ICostoTipo,
  IItemProyeccionCosto } from '../../models/Interfaces';

import * as moment from 'moment';

@Component({
  selector: 'app-costo',
  templateUrl: './costo.component.html',
  styleUrls: ['./costo.component.css'],
  animations: [fadeInAnimation],
})
export class CostoComponent implements OnInit {

  constructor(
    private route: ActivatedRoute,
    private registro_service: RegistroService,
    private core_service: CoreService,
    private proyecciones_service: ProyeccionesService,
    private presupuesto_service: PresupuestosService,
    private _notifications: NotificationService,
    private modal: Modal,
    private router: Router,
  ) { }

  centro_costo: ICentroCosto;
  periodos: Periodo[];
  tipo_costos: ICostoTipo[];

  revisiones: IProyeccionCosto[] = [];
  revision_actual: IProyeccionCosto = null;

  isDisabled = false;

  initialLoading = true;
  loadingProgress = 0;

  set_progress() {
    if (this.initialLoading) {
      this.loadingProgress += 1;
      if (this.loadingProgress > 3) {
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
      this.presupuesto_service.get_tipo_items().subscribe(tipos => {
        this.tipo_costos = tipos;
        this.set_progress();
      });
    });
  }

  refresh(obra_id?, rev?) {
    obra_id = obra_id || this.centro_costo.id;
    this.proyecciones_service
      .get_proyeccion_costo_list(obra_id)
      .subscribe(revisiones => {
        revisiones.map(revision => {
          revision.items.map(item => {
            item.monto = Number.parseFloat(String(item.monto));
          });
          revision.periodo = new Periodo(revision.periodo);
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
          this.revision_actual = new Object as IProyeccionCosto;
          this.revision_actual.periodos = [];
          this.revision_actual.items = [];
          this.revision_actual.periodo = this.periodos[this.periodos.length - 1];
          this.revision_actual.periodo_id = this.revision_actual.periodo.pk;
          this.revision_actual.centro_costo_id = this.centro_costo.id;
        }
        this.set_progress();
      });
      this.isDisabled = false;
  }

  get periodosDisponibles(): Periodo[] {
    if (this.revision_actual) {
      return this.periodos.filter(i => this.revision_actual.periodos.indexOf(i.pk) < 0);
    }
    return this.periodos || [];
  }

  getColumnClass(id_periodo) {
    let periodo = this.find_periodo(id_periodo);
    let perdiod_revision = this.find_periodo(this.revision_actual.periodo_id);
    if (periodo.fecha_fin_obj().isSame(perdiod_revision.fecha_fin_obj())) {
      return 'current';
    } else {
      if (periodo.fecha_fin_obj().isAfter(perdiod_revision.fecha_fin_obj())) {
        return 'future';
      } else {
        return 'pass';
      }
    }

  }

  items_costo(periodo_id: number, tipo_id: number): IItemProyeccionCosto {
    let item = this.revision_actual.items.find(
      i => i.periodo == periodo_id && i.tipo_costo == tipo_id);
    if (item == undefined) {
      item = this.addNewItem(periodo_id, tipo_id);
    }
    return item;
  }

  trackByIndex(index: number, item: IItemProyeccionCosto) {
    return index;
  }

  /*
    MANEJO DE TABLA
  */

  addNewItem(periodo_id: number, tipo_id: number, monto?: number) {
    let item = new Object as IItemProyeccionCosto;
    item.periodo = periodo_id;
    item.tipo_costo = tipo_id;
    if (monto) {
      item.monto = monto;
    }
    this.revision_actual.items.push(item);
    return item;
  }

  totalCosto(tipo_id): number {
    let total = 0;
    for (const item of this.revision_actual.items.filter(i => i.tipo_costo == tipo_id)) {
      if (item.monto) {
        total += Number(item.monto);
      }
    }
    return total;
  }

  totalPeriodo(periodo_id: number): number {
    let total = 0;
    for (const item of this.revision_actual.items.filter(i => i.periodo == periodo_id)) {
      if (item.monto) {
        total += Number(item.monto);
      }
    }
    return total;
  }

  totalCostoAllPeriodos(): number {
    let total = 0;
    for (const item of this.revision_actual.items) {
      if (item.monto) {
        total += Number(item.monto);
      }
    }
    return total;
  }

  addPeriodoToItems(id_periodo) {
    id_periodo = Number.parseInt(id_periodo);
    if (this.revision_actual.periodos.indexOf(id_periodo) > 0) {
      const periodo = this.find_periodo(id_periodo);
      this._notifications.error(`Ya se encuentra añadida la columna para ${periodo.descripcion}`);
      return;
    }
    for (const tipo of this.tipo_costos) {
      this.addNewItem(id_periodo, tipo.pk);
    }
    this.revision_actual.periodos.push(id_periodo);
    this.revision_actual.periodos.sort();
  }

  delPeriodoOfItemsModal(id_periodo) {
    id_periodo = Number.parseInt(id_periodo);
    const periodo = this.find_periodo(id_periodo);
    let idx = this.revision_actual.periodos.indexOf(id_periodo);
    if (idx < 0) {
      this._notifications.error(`No se encuentra la columna para ${periodo.descripcion}`);
      return;
    }
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Quitar columna')
    .message(`¿Seguro que desea quitar la columna de ${periodo.descripcion}?`)
    .cancelBtn('Cancelar')
    .okBtn('Si, quitar!')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => this.delPeriodoOfItems(id_periodo),
          () => {}
        );
      },
    );
  }

  delPeriodoOfItems(id_periodo) {
    let idx = this.revision_actual.periodos.indexOf(id_periodo);
    this.revision_actual.periodos.splice(idx, 1);

    for (const item of this.revision_actual.items.filter(i => i.periodo == id_periodo)) {
      idx = this.revision_actual.items.indexOf(item);
      if (idx > 0) {
        this.revision_actual.items.splice(idx, 1);
      }
    }
  }

  itemIsValid(item: IItemProyeccionCosto): boolean {
    if (item.periodo && item.tipo_costo) {
      if (item.monto != null && isNaN(item.monto)) {
        return false;
      }
      return true;
    }
    return false;
  }

  find_periodo(periodo_id: Number): Periodo {
    let periodo = this.periodos.find(i => i.pk == periodo_id);
    return periodo;
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


  /*
    acciones de botones
  */

  validate(): boolean {
    for (let item of this.revision_actual.items) {
      if (!this.itemIsValid(item)) {
        this._notifications.error('Corrija primero los ítems con fondo rojo.');
        return false;
      }
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
    let items = this.revision_actual.items.filter(i => this._tonum(i.monto) > 0);
    this.revision_actual.items = items;
    if (this.revision_actual.pk) {
      this.proyecciones_service.update_costo_proyeccion(this.revision_actual).subscribe(
        avance => {
          this._notifications.success('Se guardó correctamente la proyección.');
          this.refresh(this.centro_costo.id, avance.pk);
        },
        error => this.handleError(error),
        () => this.isDisabled = false
      );
    } else {
      this.proyecciones_service.create_costo_proyeccion(this.revision_actual).subscribe(
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
    let new_revision: IProyeccionCosto = Object.assign({}, this.revision_actual);
    new_revision.es_base = false;
    new_revision.base_numero = null;
    new_revision.pk = null;
    new_revision.items = this.revision_actual.items.map(
      item => {
        let new_item = new Object as IItemProyeccionCosto;
        new_item.monto = item.monto;
        new_item.tipo_costo = item.tipo_costo;
        new_item.periodo = item.periodo;
        return new_item;
      }
    );

    let items = new_revision.items.filter(i => this._tonum(i.monto) > 0);
    new_revision.items = items;

    this.proyecciones_service.create_costo_proyeccion(new_revision).subscribe(
      revision => {
        this._notifications.success('Se creó una nueva revisión de la proyección');
        this.router.navigate(['/proyecciones', this.centro_costo.id, 'costo', revision.pk]);
      },
      error => this.handleError(error)
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
    .okBtn('Si')
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
    let new_revision: IProyeccionCosto = Object.assign({}, this.revision_actual);
    new_revision.es_base = true;
    new_revision.base_numero = this.revision_actual.base_vigente + 1;
    new_revision.pk = null;
    new_revision.items = this.revision_actual.items.map(
      item => {
        let new_item = new Object as IItemProyeccionCosto;
        new_item.monto = item.monto;
        new_item.tipo_costo = item.tipo_costo;
        new_item.periodo = item.periodo;
        return new_item;
      }
    );

    let items = new_revision.items.filter(i => this._tonum(i.monto) > 0);
    new_revision.items = items;

    this.proyecciones_service.create_costo_proyeccion(new_revision).subscribe(
      revision => {
        this._notifications.success(`Se creó la nueva revisión BASE ${revision.base_numero}`);
        this.router.navigate(['/proyecciones', this.centro_costo.id, 'costo', revision.pk]);
      },
      error => this.handleError(error)
    );
  }

  deleteRevisionActual() {
    if (this.revision_actual.es_base) {
      this._notifications.error('No puede quitarse una revisión BASE.');
      return;
    }
    if (!this.revision_actual.pk) {
      this._notifications.error('Esta revisión aún no ha sido creada.');
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
            this.proyecciones_service.delete_proyeccion_costo(this.revision_actual).subscribe(
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

}
