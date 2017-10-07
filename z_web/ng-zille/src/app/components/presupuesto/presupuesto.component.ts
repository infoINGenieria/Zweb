import { itemAnim } from './../../_animations/itemAnim';
import { fadeInAnimation } from './../../_animations/fade-in.animation';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import {Router} from '@angular/router';
import 'rxjs/add/operator/map';

import { ICentroCosto, IRevision, ITipoItemPresupuesto, IPresupuesto, IItemPresupuesto } from './../../models/Interfaces';
import { ItemPresupuesto } from './../../models/ItemPresupuesto';

import { CoreService } from './../../services/core/core.service';
import { PresupuestosService } from './../../services/presupuestos/presupuestos.service';


@Component({
  selector: 'app-presupuesto',
  templateUrl: './presupuesto.component.html',
  styleUrls: ['./presupuesto.component.scss'],
  animations: [fadeInAnimation, itemAnim]
})
export class PresupuestoComponent implements OnInit {

  presupuesto: IPresupuesto;
  revision: IRevision;

  tipos: ITipoItemPresupuesto[] = [];
  centro_costos: ICentroCosto[] = [];

  loading = 0;

  constructor(
      private route: ActivatedRoute,
      private router: Router,
      private presupuestos_service: PresupuestosService,
      private core_service: CoreService
    ) {
      route.params.subscribe(val => {
        const pk = val['pk'];
        if (pk) {
          const version = val['version'];
          this.presupuestos_service.get_revision(pk, version).subscribe(revision => {
            this.revision = revision;
            this.revision.items = this.revision.items.map(item => new ItemPresupuesto(item));
            this.presupuesto = revision.presupuesto as IPresupuesto;
            this.loading += 1;
          });
        } else {
          // create empty objects
          this.presupuesto = new Object as IPresupuesto;
          this.revision = new Object as IRevision;
          this.revision.presupuesto = this.presupuesto;
          this.revision.items = Array<ItemPresupuesto>();
          this.revision.version = 0;
        }
      });
   }

   ngOnInit() {
      this.presupuestos_service.get_tipo_items().subscribe(tipos => {
        this.tipos = tipos;
        this.loading += 1;
      });

      this.core_service.get_centro_costos_list().subscribe(centros => {
        this.centro_costos = centros;
        this.loading += 1;
      });
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
    const index = this.revision.items.indexOf(item);
    this.revision.items.splice(index, 1);
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

  showItems() {
    console.log(this.presupuesto);
    console.log(this.revision);
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
    const calc = this.calc_total_items_pesos() * this._tonum(valor) / 100;
    return calc || 0;
  }

  sobre_previstos_dolares(valor: number) {
    return this.calc_total_items_dolares() * this._tonum(valor) / 100 || 0;
  }

  sobre_previstos_total(valor: number) {
    if (!this.revision.valor_dolar) {
      return 0;
    }
    return this.sobre_previstos_pesos(valor) +
      (this.sobre_previstos_dolares(valor) * this.revision.valor_dolar) || 0;
  }

  sobre_venta_pesos(valor: number) {
    return this.calc_venta_pesos() * this._tonum(valor) / 100 || 0;
  }

  sobre_venta_dolares(valor: number) {
    return this.calc_venta_dolares() * this._tonum(valor) / 100 || 0;
  }

  sobre_venta_total(valor: number) {
    if (!this.revision.valor_dolar) {
      return 0;
    }
    return this.sobre_venta_pesos(valor) +
      (this.sobre_venta_dolares(valor) * this.revision.valor_dolar) || 0;
  }

  costo_industrial_pesos() {
    let costo = this.calc_total_items_pesos();
    // contingencia
    costo += this.sobre_previstos_pesos(this.revision.contingencia);
    // Estructura no REE
    costo += this.sobre_previstos_pesos(this.revision.estructura_no_ree);
    // aval por anticipos
    costo += this.sobre_venta_pesos(this.revision.aval_por_anticipos);
    // caucion
    costo += this.sobre_venta_pesos(this.revision.seguro_caucion);
    // complimiento contrato
    costo += this.sobre_venta_pesos(this.revision.aval_por_cumplimiento_contrato);
    // cumplimiento garantia
    costo += this.sobre_venta_pesos(this.revision.aval_por_cumplimiento_garantia);
    // seguro 5
    costo += this.sobre_venta_pesos(this.revision.seguro_5);
    return costo;
  }
  costo_industrial_dolares() {
    let costo = this.calc_total_items_dolares();
    // contingencia
    costo += this.sobre_previstos_dolares(this.revision.contingencia);
    // Estructura no REE
    costo += this.sobre_previstos_dolares(this.revision.estructura_no_ree);
    // aval por anticipos
    costo += this.sobre_venta_dolares(this.revision.aval_por_anticipos);
    // caucion
    costo += this.sobre_venta_dolares(this.revision.seguro_caucion);
    // complimiento contrato
    costo += this.sobre_venta_dolares(this.revision.aval_por_cumplimiento_contrato);
    // cumplimiento garantia
    costo += this.sobre_venta_dolares(this.revision.aval_por_cumplimiento_garantia);
    // seguro 5
    costo += this.sobre_venta_dolares(this.revision.seguro_5);
    return costo;
  }

  costo_industrial_total() {
    if (!this.revision.valor_dolar) {
      return 0;
    }
    return this.costo_industrial_pesos() + (
      this.costo_industrial_dolares() * this.revision.valor_dolar);
  }

  /*
  Mark up
  */
  sobre_costo_industrial_pesos(valor: number) {
    return this.costo_industrial_pesos() * this._tonum(valor) / 100 || 0;
  }

  sobre_costo_industrial_dolares(valor: number) {
    return this.costo_industrial_dolares() * this._tonum(valor) / 100 || 0;
  }

  sobre_costo_industrial_total(valor: number) {
    if (!this.revision.valor_dolar) {
      return 0;
    }
    return this.sobre_costo_industrial_pesos(valor) +
      (this.sobre_costo_industrial_dolares(valor) * this.revision.valor_dolar) || 0;
  }

  sobre_ganancia_neta_pesos(valor: number) {
    return this.sobre_costo_industrial_pesos(this.revision.ganancias) * this._tonum(valor) / 100 || 0;
  }

  sobre_ganancia_neta_dolares(valor: number) {
    return this.sobre_costo_industrial_dolares(this.revision.ganancias) * this._tonum(valor) / 100 || 0;
  }

  sobre_ganancia_neta_total(valor: number) {
    if (!this.revision.valor_dolar) {
      return 0;
    }
    return this.sobre_ganancia_neta_pesos(valor) +
      (this.sobre_ganancia_neta_dolares(valor) * this.revision.valor_dolar) || 0;
  }


  /*
  Total venta
  */

  calc_venta_pesos() {
    let dividendo = 1 + this.get_perc_dividendo_venta();
    dividendo = dividendo * this.calc_total_items_pesos();
    const divisor = 1 - this.get_perc_sobre_venta();
    return this._tonum(dividendo / divisor);
  }

  calc_venta_dolares() {
    let dividendo = 1 + this.get_perc_dividendo_venta();
    dividendo = dividendo * this.calc_total_items_dolares();
    const divisor = 1 - this.get_perc_sobre_venta();
    return this._tonum(dividendo / divisor);
  }

  calc_venta_total() {
    if (!this.revision.valor_dolar) {
      return 0;
    }
    return this.calc_venta_pesos() +
      (this.calc_venta_dolares() * this.revision.valor_dolar) || 0;
  }
  precio_total_venta(): number {
    if (!this.revision.valor_dolar) {
      return 0;
    }
    const costo = this._tonum(this.revision.precio_venta) + (this._tonum(this.revision.precio_venta_dolar) * this.revision.valor_dolar);
    return costo;
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

  get_perc_sobre_venta(): number {
    let perc = this.revision.aval_por_anticipos || 0;
    perc += this.revision.seguro_caucion || 0;
    perc += this.revision.aval_por_cumplimiento_contrato || 0;
    perc += this.revision.aval_por_cumplimiento_garantia || 0;
    perc += this.revision.seguro_5 || 0;
    perc += this.revision.sellado || 0;
    perc += this.revision.ingresos_brutos || 0;
    perc += this.revision.impuestos_cheque || 0;
    perc = perc / 100;
    return perc;
  }

  get_perc_dividendo_venta(): number {
    let perc = this.revision.contingencia || 0;
    perc += this.revision.estructura_no_ree || 0;
    perc += this.revision.imprevistos || 0;
    perc += this.revision.ganancias || 0;
    perc += (this.revision.ganancias * this.revision.impuestos_ganancias) || 0;
    perc += this.revision.costo_financiero || 0;
    perc = perc / 100;
    return perc;
  }

  get isWarningVenta(): boolean {
    return this.calc_venta_total() > this.precio_total_venta();
  }

  create_presupuesto() {
    this.presupuesto.fecha = this.revision.fecha;
    this.presupuestos_service.create_presupuesto(this.presupuesto).subscribe(presupuesto => {
      this.presupuesto = presupuesto;
      this.revision.version = presupuesto.vigente;
      this.revision.presupuesto = this.presupuesto;
      this.presupuestos_service.save_revision(this.revision).subscribe(revision => {
        this.revision = revision;
        this.router.navigate(['/presupuestos', this.presupuesto.pk, 'v', revision.version]);
      });
    });
  }

  create_new_version() {
    this.revision.version = this.presupuesto.vigente + 1;
    this.revision.pk = null;
    this.presupuestos_service.create_revision(this.revision).subscribe(revision => {
      this.revision = revision as IRevision;
      this.presupuesto = this.revision.presupuesto as IPresupuesto;
      this.router.navigate(['/presupuestos', this.presupuesto.pk, 'v', revision.version]);
    });
  }

  save_revision() {
    this.presupuestos_service.save_revision(this.revision).subscribe(revision => {
      this.revision = revision;
    });
  }
}
