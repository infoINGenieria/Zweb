import { Periodo } from './../../models/Periodo';
import { ProyeccionesService } from './../../services/proyecciones.service';
import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute} from '@angular/router';

import { Modal } from 'ngx-modialog/plugins/bootstrap';

import { fadeInAnimation } from '../../_animations/index';

import { CoreService } from '../../services/core/core.service';
import { NotificationService } from '../../services/core/notifications.service';

import { ICentroCosto, IProyeccionAvanceObra, IItemProyeccionAvanceObra, IPeriodo } from './../../models/Interfaces';
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
    private router: Router,
    private proyecciones_service: ProyeccionesService,
    private core_service: CoreService,
    private _notifications: NotificationService,
    private modal: Modal
  ) { }

  centro_costo: ICentroCosto;
  periodos: IPeriodo[];

  revisiones: IProyeccionAvanceObra[] = [];
  revision_actual: IProyeccionAvanceObra = null;

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
    .get_proyeccion_avance_obra_list(obra_id)
    .subscribe(revisiones => {
      revisiones.map(revision => {
        revision.items.map(item => {
          item.avance = Number.parseFloat(String(item.avance));
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
        this.revision_actual = new Object as IProyeccionAvanceObra;
        this.revision_actual.items = [];
        this.revision_actual.periodo = this.periodos[this.periodos.length - 1];
        this.revision_actual.periodo_id = this.revision_actual.periodo.pk;
        this.revision_actual.centro_costo_id = this.centro_costo.id;
      }
      this.set_progress();
    });
  }

  itemIsValid(item: IItemProyeccionAvanceObra): boolean {
    if (item.periodo) {
      if (item.avance != null && isNaN(item.avance)) {
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

  find_real(item: IItemProyeccionAvanceObra) {
    if (this.revision_actual && this.revision_actual.avance_real) {
      return this.revision_actual.avance_real.find((i) => {
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

  acumulado(item: IItemProyeccionAvanceObra): number {
    const posicion = this.revision_actual.items.indexOf(item);
    let acumulado = 0.0;
    for (const av of this.revision_actual.items.slice(0, posicion + 1)) {
      acumulado += this._tonum(av.avance);
    }
    return acumulado;
  }

  acumuladoConsolidado(item: IItemProyeccionAvanceObra): number {
    /*
      Suma acumulado de los datos reales y, cuando estos no existan,
      la proyección del mes correspondiente.
    */
    const posicion = this.revision_actual.items.indexOf(item);
    let acumulado = 0.0;
    for (const av of this.revision_actual.items.slice(0, posicion + 1)) {
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
    let item = new Object as IItemProyeccionAvanceObra;
    this.revision_actual.items.push(item);
  }

  validate() :boolean {
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

  guardarActual() {
    if (!this.validate()) {
      return;
    }
    this.isDisabled = true;

    if (this.revision_actual.pk) {
      this.proyecciones_service.update_avance_obra_proyeccion(this.revision_actual).subscribe(
        avance => {
          this._notifications.success('Se guardó correctamente la proyección.');
          this.refresh(this.centro_costo.id, avance.pk);
        },
        error => this.handleError(error),
        () => this.isDisabled = false
      );
    } else {
      this.proyecciones_service.create_avance_obra_proyeccion(this.revision_actual).subscribe(
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
    const msg = `Está a punto de crear una nueva revisión de la proyección como ` +
                `ajuste de <b>${periodo.descripcion}</b>. ¿Continuar?`;
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Crear nueva revisión')
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
    let new_revision: IProyeccionAvanceObra = Object.assign({}, this.revision_actual);
    new_revision.es_base = false;
    new_revision.base_numero = null;
    new_revision.pk = null;
    new_revision.items = this.revision_actual.items.map(
      item => {
        let new_item = new Object as IItemProyeccionAvanceObra;
        new_item.avance = item.avance;
        new_item.periodo = item.periodo;
        return new_item;
      }
    );
    this.proyecciones_service.create_avance_obra_proyeccion(new_revision).subscribe(
      revision => {
        this._notifications.success('Se creó una nueva revisión de la proyección');
        this.router.navigate(['/proyecciones', this.centro_costo.id, 'avances-obra', revision.pk]);
      },
      error => this.handleError(error)
    );
  }

  eliminarAvanceObra(obj: IItemProyeccionAvanceObra) {
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Quitar ítem')
    .message(
      '¿Está seguro que desea <b>quitar</b> este ítem de la proyección ' +
      'de avance de obra del sistema?<br><b>Esta acción se confirmará al guardar.</b>')
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

  trackByIndex(index: number, item: IItemProyeccionAvanceObra) {
    return index;
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
  }

  establecerComoBase() {
    if (!this.validate()) {
      return;
    }
    if (this.revision_actual.es_base) {
      this._notifications.error('Esta revisión ya es BASE.');
      return;
    }
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Establecer revisión como BASE')
    .message(`¿Está seguro que desea <b>establecer como BASE</b> esta revisión?`)
    .cancelBtn('Cancelar')
    .okBtn('Si, establecer!')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => {
            this.proyecciones_service.hacer_vigente_avance_obra_proyeccion(this.revision_actual).subscribe(
              r => {
                this.refresh(this.centro_costo.id, this.revision_actual.pk);
                this._notifications.success(`La revisión fue establecida como BASE ${r.base_numero}.`);
              },
              error => this.handleError(error));
          },
          () => {}
        );
      },
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
    .message(`¿Está seguro que desea <b>eliminar</b> esta revisión de la proyección del sistema?` +
             `<br><b>Esta acción no puede deshacerse.</b>`)
    .cancelBtn('Cancelar')
    .okBtn('Eliminar')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => {
            this.proyecciones_service.delete_proyeccion_avance_obra(this.revision_actual).subscribe(
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
