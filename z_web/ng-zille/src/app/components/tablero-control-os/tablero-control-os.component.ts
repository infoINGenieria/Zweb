import { TableroService } from './../../services/tablero.service';
import { NotificationService } from './../../services/core/notifications.service';
import { ICentroCosto, IPeriodo } from './../../models/Interfaces';
import { CoreService } from './../../services/core/core.service';
import { Component, OnInit, ViewEncapsulation } from '@angular/core';

declare let d3: any;

@Component({
  selector: 'app-tablero-control-os',
  templateUrl: './tablero-control-os.component.html',
  styleUrls: ['./tablero-control-os.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class TableroControlOsComponent implements OnInit {

  periodos: IPeriodo[] = [];
  periodo: IPeriodo;
  centro_costos: ICentroCosto[] = [];
  centro_costo: ICentroCosto;

  data: any = null;

  // feo pero funciona. Estos haeders sirven para iterar en cada subconjunto
  headers = ['acumulado', 'faltante_estimado', 'faltante_presupuesto',
             'estimado', 'presupuesto', 'comercial'];


  g_cert_options = null;
  graph_data = null;

  g_costo_options = null;
  graph_costo_data = null;

  g_avance_options = null;
  graph_avance_data = null;

  g_consol_options = null;
  graph_consol_data = null;
  constructor(
    private _coreServ: CoreService,
    private _tableroServ: TableroService,
    private _notifications: NotificationService
  ) { }

  ngOnInit() {
    this._coreServ.get_centro_costos_list().subscribe(cc => {
      this.centro_costos = cc as ICentroCosto[];
    });
    this._coreServ.get_periodos_list().subscribe(p => {
      this.periodos = p as IPeriodo[];
    });

    this.g_cert_options = {
      chart: {
        type: 'lineChart',
        height: 350,
        margin : {
          top: 80,
          right: 80,
          bottom: 60,
          left: 80
        },
        x: function(d){ return d.x; },
        y: function(d){ return d.y; },
        useInteractiveGuideline: true,
        // interpolate: 'basis',
        showLegend: true,
        xAxis: {
          axisLabel: 'Periodo',
          tickFormat: function(d){
            return d3.time.format('%Y-%m')( new Date(d));
          }
        },
        yAxis: {
          axisLabel: 'Pesos ($)',
          tickFormat: function(d){
            return '$ ' + d3.format(',.2f')(d);
          },
          // axisLabelDistance: -10
        }
      }
    };
    this.g_costo_options = {
      chart: {
        type: 'lineChart',
        height: 350,
        margin : {
          top: 80,
          right: 80,
          bottom: 60,
          left: 80
        },
        x: function(d){ return d.x; },
        y: function(d){ return d.y; },
        useInteractiveGuideline: true,
        // interpolate: 'basis',
        showLegend: true,
        xAxis: {
          axisLabel: 'Periodo',
          tickFormat: function(d){
            return d3.time.format('%Y-%m')( new Date(d));
          }
        },
        yAxis: {
          axisLabel: 'Pesos ($)',
          tickFormat: function(d){
            return '$ ' + d3.format(',.2f')(d);
          },
          // axisLabelDistance: -10
        }
      }
    };

    this.g_avance_options = {
      chart: {
        type: 'lineChart',
        height: 350,
        margin : {
          top: 80,
          right: 80,
          bottom: 60,
          left: 80
        },
        x: function(d){ return d.x; },
        y: function(d){ return d.y; },
        useInteractiveGuideline: true,
        // interpolate: 'basis',
        showLegend: true,
        xAxis: {
          axisLabel: 'Periodo',
          tickFormat: function(d){
            return d3.time.format('%Y-%m')( new Date(d));
          }
        },
        yAxis: {
          axisLabel: 'Avance de obra (%)',
          tickFormat: function(d){
            return d3.format('.2f')(d) + ' %';
          },
          // axisLabelDistance: -10
        },
        yDomain: [0, 100]
      }
    };
    this.g_consol_options = {
      chart: {
        type: 'lineChart',
        height: 450,
        margin : {
          top: 80,
          right: 80,
          bottom: 60,
          left: 120
        },
        x: function(d){ return d.x; },
        y: function(d){ return d.y; },
        useInteractiveGuideline: true,
        // interpolate: 'basis',
        showLegend: true,
        xAxis: {
          axisLabel: 'Periodo',
          tickFormat: function(d){
            return d3.time.format('%Y-%m')( new Date(d));
          }
        },
        yAxis: {
          // axisLabel: 'Pesos ($)',
          tickFormat: function(d){
            return '$ ' + d3.format(',.2f')(d);
          },
          // axisLabelDistance: -10
        },
        // yDomain: [0]
      }
    };
  }

  showTablero() {
    if (this.centro_costo && this.periodo) {
      this._tableroServ.get_data_table(this.centro_costo, this.periodo).subscribe(
        data => {
          this.data = data;
          this.get_data_graphs();
        },
        error => {
          this.data = null;
          this.handleError(error);
        }
      );

    } else {
      this._notifications.warning('Debe seleccionar un proyecto y el periodo.');
    }
  }

  get_data_graphs() {
    this._tableroServ.get_graph_certificacion(this.centro_costo).subscribe(
      data => {
        setTimeout(() => this.graph_data = data, 1000);
      },
      error => {
        this.graph_data = null;
        this.handleError(error);
      }
    );
    this._tableroServ.get_graph_costo(this.centro_costo).subscribe(
      data => {
        setTimeout(() => this.graph_costo_data = data, 1000);
      },
      error => {
        this.graph_costo_data = null;
        this.handleError(error);
      }
    );
    this._tableroServ.get_graph_avance(this.centro_costo).subscribe(
      data => {
        setTimeout(() => this.graph_avance_data = data, 1000);
      },
      error => {
        this.graph_avance_data = null;
        this.handleError(error);
      }
    );
    this._tableroServ.get_graph_consolidado(this.centro_costo).subscribe(
      data => {
        this.graph_consol_data = data;
      },
      error => {
        this.graph_consol_data = null;
        this.handleError(error);
      }
    );
  }

  get_items_costos(): String[] {
    try {
      let keys = Object.keys(this.data['costos']['acumulado']);
      keys.splice(keys.indexOf('subtotal'));
      keys.splice(keys.indexOf('total_costos'));
      return keys;
    } catch (e) {
      return [];
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
}
