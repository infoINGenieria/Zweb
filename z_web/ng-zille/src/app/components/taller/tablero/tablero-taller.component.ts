import { CoreService } from './../../../services/core/core.service';
import { IPeriodo, IEquipoCostoTaller, ITotalFlota } from './../../../models/Interfaces';
import { Component, OnInit } from '@angular/core';
import { TallerService } from '../../../services/taller.service';

@Component({
  selector: 'app-tablero-taller',
  templateUrl: './tablero-taller.component.html',
  styleUrls: ['./tablero-taller.component.css']
})
export class TableroTallerComponent implements OnInit {

  showing_data = false;
  refreshTotal = false;
  periodos: IPeriodo[] = [];
  periodo: IPeriodo;

  data: IEquipoCostoTaller[] = [];

  totalFLota: ITotalFlota = null;
  filtro_equipo: string;

  constructor(
    public tallerServ: TallerService,
    public coreServ: CoreService
  ) { }

  ngOnInit() {
    this.coreServ.get_periodos_list().subscribe(
      periodos => this.periodos = periodos as IPeriodo[],
      err => console.log(err)
    );
  }

  get equiposCostos() {
    if (this.filtro_equipo) {
      return this.data.filter(a => {
        // tslint:disable-next-line:max-line-length
        return a.equipo != null && (
          a.equipo.n_interno.toLowerCase().startsWith(this.filtro_equipo.toLowerCase()) ||
          a.equipo.n_interno.toLowerCase().endsWith(this.filtro_equipo.toLowerCase()) ||
          a.equipo.dominio.toLowerCase().startsWith(this.filtro_equipo.toLowerCase()) ||
          a.equipo.dominio.toLowerCase().endsWith(this.filtro_equipo.toLowerCase()
          ));
      });
    } else {
      return this.data.filter(eq => eq.equipo != null);
    }
  }

  calcularMonto() {
    let monto = 0;
    for (let i = 0; i < this.data.length; i++) {
      monto += Number(this.data[i].costo_mensual_del_activo_calculado);
    }
    return monto;
  }

  get_tablero_taller() {
    this.tallerServ.get_tablero_costo_taller(this.periodo).subscribe(
      data => {
        console.log('data', data);
        this.data = data as IEquipoCostoTaller[];
        this.totalFLota = new Object as ITotalFlota;
        this.totalFLota.cantidad = this.data.length;
        this.totalFLota.monto = this.calcularMonto();
        console.log(this.totalFLota);
        this.showing_data = true;
      },
      err => console.log(err)
    );


  }

  cerrarTablero() {
    this.data = [];
    this.showing_data = false;
  }

  recalcularFlota() {
    if (!this.refreshTotal) {
      this.refreshTotal = true;
      this.tallerServ.get_tablero_costo_taller_total_flota(this.periodo).subscribe(
        data => {
          this.totalFLota = data;
          this.refreshTotal = false;
          this.tallerServ.get_tablero_costo_taller(this.periodo).subscribe(
            d => this.data = d as IEquipoCostoTaller[],
            err => console.log(err)
          );
        }
      );
    }
  }
}
