// import { IMyDpOptions, IMyDateModel, IMyDate } from 'mydatepicker';
import { Modal } from 'ngx-modialog/plugins/bootstrap';
import { itemAnim } from './../../_animations/itemAnim';
import { fadeInAnimation } from './../../_animations/fade-in.animation';
import { Component, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import {Router} from '@angular/router';
import 'rxjs/add/operator/map';
import { DatePickerComponent, IDatePickerConfig, ECalendarValue } from 'ng2-date-picker';
import * as moment from 'moment';

import { ICentroCosto, IRevision, ICostoTipo, IPresupuesto, IItemPresupuesto } from './../../models/Interfaces';
import { ItemPresupuesto } from './../../models/ItemPresupuesto';

import { CoreService } from './../../services/core/core.service';
import { PresupuestosService } from './../../services/presupuestos/presupuestos.service';
import { NotificationService } from './../../services/core/notifications.service';



@Component({
  selector: 'app-presupuesto',
  templateUrl: './presupuesto.component.html',
  styleUrls: ['./presupuesto.component.scss'],
  animations: [fadeInAnimation, itemAnim]
})
export class PresupuestoComponent implements OnInit {

  presupuesto: IPresupuesto;
  revision: IRevision;

  tipos: ICostoTipo[] = [];
  centro_costos: ICentroCosto[] = [];

  loading = 0;

  datePickerConfig: IDatePickerConfig = {
    'format': 'DD/MM/YYYY',
    'drops': 'down',
    'locale': 'es',
    'returnedValueType': ECalendarValue.String
  };

  constructor(
      private route: ActivatedRoute,
      private router: Router,
      private presupuestos_service: PresupuestosService,
      private core_service: CoreService,
      private notify_service: NotificationService,
      private modal: Modal
    ) {
      route.params.subscribe(val => {
        const pk = val['pk'];
        if (pk) {
          const version = val['version'];
          this.presupuestos_service.get_revision(pk, version).subscribe(revision => {
            this.revision = revision;
            this.revision.items = this.revision.items.map(item => new ItemPresupuesto(item));
            this.presupuesto = revision.presupuesto as IPresupuesto;
            this.setInProgress(1);
          });
        } else {
          // create empty objects
          this.presupuesto = new Object as IPresupuesto;
          this.revision = new Object as IRevision;
          this.revision.presupuesto = this.presupuesto;
          this.revision.items = Array<IItemPresupuesto>();
          this.revision.version = 0;
        }
      });
   }

   ngOnInit() {
      this.presupuestos_service.get_tipo_items().subscribe(tipos => {
        this.tipos = tipos;
        this.setInProgress(1);
      });

      this.core_service.get_centro_costos_list().subscribe(centros => {
        this.centro_costos = centros;
        this.setInProgress(1);
      });
   }

   setInProgress(amount: number) {
     setTimeout(() => this.loading += amount, 50);
   }

   handleError(error: any) {
    this.notify_service.error(error._body || error);
  }

  addItem(indirecto: boolean) {
    const item = new ItemPresupuesto();
    if (indirecto) {
      item.indirecto = true;
      this.revision.items.push(item);
    } else {
      this.revision.items.push(item);
    }
  }

  itemIsValid(item: IItemPresupuesto): boolean {
    if (item.tipo != null) {
      if (this._tonum(item.dolares) + this._tonum(item.pesos) > 0) {
        return true;
      }
    }
    return false;
  }

  checkAllItem(): boolean {
    for (const item of this.revision.items) {
      if (!this.itemIsValid(item)) {
        return false;
      }
    }
    return true;
  }

  removeItem(item: IItemPresupuesto) {
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
            const index = this.revision.items.indexOf(item);
            this.revision.items.splice(index, 1);
          },
          () => {}
        );
      },
    );
  }

  get items_directos(): Array<IItemPresupuesto> {
      return this.revision.items.filter(item => item.indirecto === false);
  }

  get items_indirectos(): Array<IItemPresupuesto> {
      return this.revision.items.filter(item => item.indirecto === true);
  }

  trackByIndex(index: number, item: ItemPresupuesto) {
    if (item && item.pk) {
      return item.pk;
    }
    return index;
  }

  /*
  Ventas
  */

  calc_total_venta(): number {
    return this._tonum(this.revision.venta_contractual_b0) + this._tonum(this.revision.ordenes_cambio) +
      this._tonum(this.revision.reajustes_precio) + this._tonum(this.revision.reclamos_reconocidos);
  }

  /*
  Items de costos
  */
  calc_subtotal_row(item: ItemPresupuesto): number {
    if (!this.revision.valor_dolar) {
      return 0;
    }
    const calc = this._tonum(item.pesos) + this._tonum(item.dolares) * this.revision.valor_dolar;
    return calc;
  }

  /* directos */
  calc_total_items_pesos_directo(): number {
    let total = 0;
    for (const item of this.items_directos) {
      total += Number(item.pesos);
    }
    return total;
  }

  calc_total_items_dolares_directo(): number {
    let total = 0;
    for (const item of this.items_directos) {
        total += Number(item.dolares);
    }
    return total;
  }

  calc_total_items_directo(): number {
    if (!this.revision.valor_dolar) {
      return 0;
    }
    return this.calc_total_items_pesos_directo() + (
      this.calc_total_items_dolares_directo() * this.revision.valor_dolar);
  }

  /* indirectos */
  calc_total_items_pesos_indirectos(): number {
    let total = 0;
    for (const item of this.items_indirectos) {
      total += Number(item.pesos);
    }
    return total;
  }

  calc_total_items_dolares_indirectos(): number {
    let total = 0;
    for (const item of this.items_indirectos) {
        total += Number(item.dolares);
    }
    return total;
  }

  calc_total_items_indirectos(): number {
    if (!this.revision.valor_dolar) {
      return 0;
    }
    return this.calc_total_items_pesos_indirectos() + (
        this.calc_total_items_dolares_indirectos() * this.revision.valor_dolar);
  }

  /* totales */
  calc_total_items_pesos(): number {
    let total = 0;
    for (const item of this.revision.items) {
      total += Number(item.pesos);
    }
    return total;
  }

  calc_total_items_dolares(): number {
    let total = 0;
    for (const item of this.revision.items) {
        total += Number(item.dolares);
    }
    return total;
  }

  calc_total_items(): number {
    if (!this.revision.valor_dolar) {
      return 0;
    }
    return this.calc_total_items_pesos() + (this.calc_total_items_dolares() * this.revision.valor_dolar);
  }

  /*
  Costos industriales
  */

  sobre_previstos_pesos(valor: number) {
    const calc = this._tonum(valor) / this.calc_total_items() * 100;
    return calc || 0;
  }

  sobre_venta_pesos(valor: number) {
    return  this._tonum(valor) / this._tonum(this.calc_total_venta()) * 100 || 0;
  }

  perc_de_venta_pesos(valor: number) {
    return  this._tonum(this.calc_total_venta()) * this._tonum(valor) / 100 || 0;
  }

  costo_industrial_pesos() {
    let costo = this.calc_total_items_pesos();
    // contingencia
    costo += this._tonum(this.revision.contingencia);
    // Estructura no REE
    costo += this._tonum(this.revision.estructura_no_ree);
    // aval por anticipos
    costo += this._tonum(this.revision.aval_por_anticipos);
    // caucion
    costo += this._tonum(this.revision.seguro_caucion);
    // complimiento contrato
    costo += this._tonum(this.revision.aval_por_cumplimiento_contrato);
    // cumplimiento garantia
    costo += this._tonum(this.revision.aval_por_cumplimiento_garantia);
    // seguro 5
    costo += this._tonum(this.revision.seguro_5);
    return costo;
  }

  /*
  Mark up
  */
  sobre_costo_industrial_pesos(valor: number) {
    return this.costo_industrial_pesos() * this._tonum(valor) / 100 || 0;
  }


  // sobre_costo_industrial_dolares(valor: number) {
  //   return this.costo_industrial_dolares() * this._tonum(valor) / 100 || 0;
  // }

  // sobre_costo_industrial_total(valor: number) {
  //   if (!this.revision.valor_dolar) {
  //     return 0;
  //   }
  //   return this.sobre_costo_industrial_pesos(valor) +
  //     (this.sobre_costo_industrial_dolares(valor) * this.revision.valor_dolar) || 0;
  // }

  calcular_ganancia() {
    let ganancia = this.calc_total_venta();
    ganancia -= this.sobre_costo_industrial_pesos(this.revision.imprevistos); // imprevistos
    ganancia -= this.perc_de_venta_pesos(this.revision.sellado);  // sellado
    ganancia -= this.perc_de_venta_pesos(this.revision.ingresos_brutos);  // iibb
    ganancia -= this.perc_de_venta_pesos(this.revision.impuestos_cheque); // cheques
    ganancia -= this.sobre_costo_industrial_pesos(this.revision.costo_financiero);  // costo financiero
    ganancia -= this.costo_industrial_pesos();
    ganancia = ganancia / (1 + (this.revision.impuestos_ganancias / 100));
    return ganancia;
  }

  calcular_perc_ganancia() {
    return this.calcular_ganancia() / this.costo_industrial_pesos() * 100;
  }

  sobre_ganancia_neta_pesos(valor: number) {
    return this.calcular_ganancia() * this._tonum(valor) / 100 || 0;
  }

  // sobre_ganancia_neta_dolares(valor: number) {
  //   return this.sobre_costo_industrial_dolares(this.revision.ganancias) * this._tonum(valor) / 100 || 0;
  // }

  // sobre_ganancia_neta_total(valor: number) {
  //   if (!this.revision.valor_dolar) {
  //     return 0;
  //   }
  //   return this.sobre_ganancia_neta_pesos(valor) +
  //     (this.sobre_ganancia_neta_dolares(valor) * this.revision.valor_dolar) || 0;
  // }


  get markup_pesos() {
    return this.calc_total_venta() - this.costo_industrial_pesos();
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



  get isWarningVenta(): boolean {
    return this.markup_pesos < 0;
  }

  create_presupuesto_modal() {
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Crear presupuesto')
    .message(`Está a punto de crear un nuevo presupuesto ¿Continuar?`)
    .cancelBtn('Cancelar')
    .okBtn('Si, crear!')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => this.create_presupuesto(),
          () => {}
        );
      },
    );
  }

  create_presupuesto() {
    // this.revision.fecha = moment(this.revision.fecha).format('DD/MM/YYYY');
    this.presupuesto.fecha = this.revision.fecha;
    this.presupuestos_service.create_presupuesto(this.presupuesto).subscribe(presupuesto => {
      this.presupuesto = presupuesto;
      this.revision.version = presupuesto.vigente;
      this.revision.presupuesto = this.presupuesto;
      // this.revision.fecha = moment(this.revision.fecha).format('DD/MM/YYYY');
      console.log(this.revision);
      this.presupuestos_service.save_revision(this.revision).subscribe(revision => {
        this.revision = revision;
        this.notify_service.success('Presupuesto guardado correctamente.');
        this.router.navigate(['/presupuestos', this.presupuesto.pk, 'v', revision.version]);
      }, error => this.handleError(error));
    }, error => this.handleError(error));
  }

  create_new_version_modal() {
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Crear nueva revisión')
    .message(`Está a punto de crear una nueva revisión del presente presupuesto ¿Continuar?`)
    .cancelBtn('Cancelar')
    .okBtn('Si, crear!')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => this.create_new_version(),
          () => {}
        );
      },
    );
  }

  create_new_version() {
    let revision_copy: IRevision = Object.assign({}, this.revision);
    revision_copy.version = this.presupuesto.vigente + 1;
    revision_copy.pk = null;
    // pesificar items
    revision_copy.items = revision_copy.items.map(item => {
      item.pesos = this.calc_subtotal_row(new ItemPresupuesto(item));
      item.dolares = 0;
      return new ItemPresupuesto(item);
    });
    // pesificación estructura
    this.presupuestos_service.create_revision(revision_copy).subscribe(revision => {
       this.revision = revision as IRevision;
       this.presupuesto = this.revision.presupuesto as IPresupuesto;
       this.notify_service.success(`Se creó la nueva revisión R${revision.version} del presupuesto.`);
       this.router.navigate(['/presupuestos', this.presupuesto.pk, 'v', revision.version]);
    }, error => this.handleError(error));
  }

  save_revision_modal() {
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Guardar revisión')
    .message(`¿Guardar la revisión actual?`)
    .cancelBtn('Cancelar')
    .okBtn('Si, guardar!')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => this.save_revision(),
          () => {}
        );
      },
    );
  }

  save_revision() {
    this.presupuestos_service.save_revision(this.revision).subscribe(revision => {
      this.revision = revision;
      this.notify_service.success(`Presupuesto actualizado correctamente.`);
    }, error => this.handleError(error));
  }
}
