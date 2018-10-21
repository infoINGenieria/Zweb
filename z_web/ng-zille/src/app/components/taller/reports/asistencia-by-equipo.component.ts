import { TallerComponent } from './../taller.component';
import { fadeInAnimation } from './../../../_animations/fade-in.animation';
import { IPeriodo, ReporteAsistenciaItemByEquipo, IEquipo, ICentroCosto } from './../../../models/Interfaces';
import { TallerService } from './../../../services/taller.service';
import { Component, OnInit } from '@angular/core';
import { CoreService } from '../../../services/core/core.service';
import { NotificationService } from '../../../services/core/notifications.service';

@Component({
  selector: 'app-asistencia-by-equipo',
  templateUrl: './asistencia-by-equipo.component.html',
  styleUrls: ['./asistencia-by-equipo.component.css'],
  animations: [fadeInAnimation]
})
export class AsistenciaByEquipoComponent implements OnInit {

  asistencias: ReporteAsistenciaItemByEquipo[] = [];
  periodos: IPeriodo[] = [];
  periodo: IPeriodo;
  centro_costos: ICentroCosto[] = [];
  centro_costo: ICentroCosto;
  equipo_id: number;
  filtered = false;

  constructor(
    private tallerServ: TallerService,
    private coreServ: CoreService,
    private _notifications: NotificationService
  ) { }

  ngOnInit() {
    this.coreServ.get_periodos_list().subscribe(
      periodos => this.periodos = periodos
    );

    this.coreServ.get_centro_costos_list().subscribe(
      ccs => this.centro_costos = ccs
    );
  }

  ver_reporte() {
    if (this.periodo) {

      this.tallerServ.get_reporte_asistencias_by_equipo(this.periodo).subscribe(
        reg => {
          this.asistencias = reg as ReporteAsistenciaItemByEquipo[];
          this.filtered = true;
        },
        err => this.handleError(err)
      );
    }
  }

  handleError(error: any) {
    try {
      const _error = JSON.parse(error._body);
      this._notifications.error(_error.detail);
    } catch (ex) {
      this._notifications.error(error._body || error);
    }
  }

  get asistencias_process(): ReporteAsistenciaItemByEquipo[] {
    let _asistencias = this.asistencias;
    if (this.equipo_id) {
      _asistencias = _asistencias.filter(a => a.equipo_id === this.equipo_id);
    }
    if (this.centro_costo) {
      _asistencias = _asistencias.filter(a => a.centro_costo_id === this.centro_costo.id);
    }
    return _asistencias;
  }

  get get_equipo() {
    if (this.equipo_id) {
      const asist = this.asistencias.find(a => a.equipo_id === this.equipo_id);
      return `${asist.equipo.equipo} (${asist.equipo.n_interno})`;
    }
    return 'Sin filtro';
  }

  resetEquipo() {
    this.equipo_id = null;
  }

  setEquipo(equipo: number) {
    this.equipo_id = equipo;
  }

  resetCC() {
    this.centro_costo = null;
  }

  setCC(cc: number) {
    this.centro_costo = this.centro_costos.find(a => a.id === cc);
  }

  /* Totales */
  get dias_total() {
    let total = 0;
    this.asistencias_process.forEach(
      item => total += item.dias
    );
    return total;
  }

  get costo_hs_total() {
    let total = 0;
    this.asistencias_process.forEach(
      item => total += Number.parseFloat(item.costo_hs + '')
    );
    return total;
  }

  get costo_diario_total() {
    let total = 0;
    this.asistencias_process.forEach(
      item => total += Number.parseFloat('' + item.costo_diario)
    );
    return total;
  }

  get costo_total() {
    let total = 0;
    this.asistencias_process.forEach(
      item => total += Number.parseFloat('' + item.costo_total)
    );
    return total;
  }

  download_report() {
    window.open(this.tallerServ.download_reporte_asistencias_summary(this.periodo), '_blank');
  }

  download_report_by_cc() {
    if (this.centro_costo) {
      const url = this.tallerServ.download_reporte_asistencias_by_cc(this.periodo, this.centro_costo);
      window.open(url, '_blank');
    }
  }
}
