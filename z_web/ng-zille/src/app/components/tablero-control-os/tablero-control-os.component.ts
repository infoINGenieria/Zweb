import { TableroService } from './../../services/tablero.service';
import { NotificationService } from './../../services/core/notifications.service';
import { ICentroCosto, IPeriodo } from './../../models/Interfaces';
import { CoreService } from './../../services/core/core.service';
import { Component, OnInit, ViewEncapsulation } from '@angular/core';

import * as moment from 'moment';
declare let d3: any;

let periodoGlobal: IPeriodo;

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

  certCallBack(chart) {
    setTimeout(function() {
      // drawing the line
      const fecha = moment(periodoGlobal.fecha_fin, 'DD/MM/YYYY').add(1, 'months').startOf('month');
      console.log(fecha);
      const limit = fecha.toDate().getTime();
      const xgrid = [limit];
      if (!chart.container) {
        return;
      }

      const max_value = d3.max([
        d3.max(chart.container.__data__[0].values, function (d) { return d.y; }),
        d3.max(chart.container.__data__[1].values, function (d) { return d.y; })
      ]);
      let custLine = d3.select('#nvd3-graph-cert')
        .select('.nv-multibar')
        .append('g');

      custLine.selectAll('line')
        .data(xgrid)
        .enter()
        .append('line')
        .attr({
          x1: function (d) { return chart.xAxis.scale()(d); },
          y1: function (d) { return chart.yAxis.scale()(0); },
          x2: function (d) { return chart.xAxis.scale()(d); },
          y2: function (d) { return chart.yAxis.scale()(max_value); }
        })
        .style('stroke', '#FF0000')
        .style('stroke-dasharray', '5,5')
        .style('stroke-width', '2px')
        ;

      // resize the chart with vertical lines
      // but only the third line will be scaled properly...
      nv.utils.windowResize(function () {
        chart.update();
        custLine.selectAll('line')
          .transition()
          .attr({
            x1: function (d) { return chart.xAxis.scale()(d); },
            y1: function (d) { return chart.yAxis.scale()(0); },
            x2: function (d) { return chart.xAxis.scale()(d); },
            y2: function (d) { return chart.yAxis.scale()(max_value); }
          });
      });
    }, 500);
  }

  avanceCallBack(chart) {
    setTimeout(function() {
      // drawing the line
      const fecha = moment(periodoGlobal.fecha_fin, 'DD/MM/YYYY').startOf('month');
      let limit = fecha.toDate().getTime();
      const xgrid = [limit];

      let custLine = d3.select('#nvd3-graph-avance')
        .select('.nv-linesWrap')
        .append('g');

      custLine.selectAll('line')
        .data(xgrid)
        .enter()
        .append('line')
        .attr({
          x1: function (d) { return chart.xAxis.scale()(d); },
          y1: function (d) { return chart.yAxis.scale()(0); },
          x2: function (d) { return chart.xAxis.scale()(d); },
          y2: function (d) { return chart.yAxis.scale()(100); }
        })
        .style('stroke', '#FF0000')
        .style('stroke-dasharray', '5,5')
        .style('stroke-width', '2px')
        ;

      chart.xScale(d3.time.scale());
      chart.update();

      // resize the chart with vertical lines
      // but only the third line will be scaled properly...
      nv.utils.windowResize(function () {
        chart.update();
        custLine.selectAll('line')
          .transition()
          .attr({
            x1: function (d) { return chart.xAxis.scale()(d); },
            y1: function (d) { return chart.yAxis.scale()(0); },
            x2: function (d) { return chart.xAxis.scale()(d); },
            y2: function (d) { return chart.yAxis.scale()(100); }
          });
      });
    }, 500);
  }

  costosCallBack(chart) {
    setTimeout(function() {
      // drawing the line
      const fecha = moment(periodoGlobal.fecha_fin, 'DD/MM/YYYY').add(1, 'months').startOf('month');
      const limit = fecha.toDate().getTime();

      const xgrid = [limit];
      let custLine = d3.select('#nvd3-graph-costo')
        .select('.nv-multibar')
        .append('g');
      if (!chart.container) {
        return;
      }

      const max_value = d3.max([
        d3.max(chart.container.__data__[0].values, function (d) { return d.y; }),
        d3.max(chart.container.__data__[1].values, function (d) { return d.y; })
      ]);

      custLine.selectAll('line')
        .data(xgrid)
        .enter()
        .append('line')
        .attr({
          x1: function (d) { return chart.xAxis.scale()(d); },
          y1: function (d) { return chart.yAxis.scale()(0); },
          x2: function (d) { return chart.xAxis.scale()(d); },
          y2: function (d) { return chart.yAxis.scale()(max_value); }
        })
        .style('stroke', '#FF0000')
        .style('stroke-dasharray', '5,5')
        .style('stroke-width', '2px')
        ;

      // resize the chart with vertical lines
      // but only the third line will be scaled properly...
      nv.utils.windowResize(function () {
        chart.update();
        custLine.selectAll('line')
          .transition()
          .attr({
            x1: function (d) { return chart.xAxis.scale()(d); },
            y1: function (d) { return chart.yAxis.scale()(0); },
            x2: function (d) { return chart.xAxis.scale()(d); },
            y2: function (d) { return chart.yAxis.scale()(max_value); }
          });
      });
    }, 500);
  }

  consolidadoCallBack(chart) {
    setTimeout(function() {
      // drawing the line
      const fecha = moment(periodoGlobal.fecha_fin, 'DD/MM/YYYY').startOf('month');
      const limit = fecha.toDate().getTime();

      const xgrid = [limit];
      let custLine = d3.select('#nvd3-graph-consolidado')
        .select('.nv-linesWrap')
        .append('g');
      if (!chart.container) {
        return;
      }
      const dataset = chart.container.__data__;

      chart.xScale(d3.time.scale());
      chart.update();

      // hacer linea
      const max_value = d3.max([
        d3.max(dataset[0].values, function (d) { return d.y; }),
        d3.max(dataset[1].values, function (d) { return d.y; })
      ]);

      custLine.selectAll('line')
        .data(xgrid)
        .enter()
        .append('line')
        .attr({
          x1: function (d) { return chart.xAxis.scale()(d); },
          y1: function (d) { return chart.yAxis.scale()(0); },
          x2: function (d) { return chart.xAxis.scale()(d); },
          y2: function (d) { return chart.yAxis.scale()(max_value); }
        })
        .style('stroke', '#FF0000')
        .style('stroke-dasharray', '5,5')
        .style('stroke-width', '2px')
        ;

      // resize the chart with vertical lines
      // but only the third line will be scaled properly...
      nv.utils.windowResize(function () {
        chart.update();
        custLine.selectAll('line')
          .transition()
          .attr({
            x1: function (d) { return chart.xAxis.scale()(d); },
            y1: function (d) { return chart.yAxis.scale()(0); },
            x2: function (d) { return chart.xAxis.scale()(d); },
            y2: function (d) { return chart.yAxis.scale()(max_value); }
          });
      });

    }, 500);
  }

  ngOnInit() {
    this._coreServ.get_centro_costos_list().subscribe(cc => {
      this.centro_costos = cc as ICentroCosto[];
    });
    this._coreServ.get_periodos_list().subscribe(p => {
      this.periodos = p as IPeriodo[];
    });

    this.g_cert_options = {
      chart: {
        type: 'multiBarChart',
        height: 450,
        margin: {
          top: 60,
          right: 30,
          bottom: 60,
          left: 120
        },
        x: function (d) { return d.x; },
        y: function (d) { return d.y; },
        stacked: false,
        showLegend: true,
        duration: 500,
        showControls: false,
        reduceXticks: false,
        xAxis: {
          axisLabel: 'Periodo',
          tickFormat: function (d) {
            return d3.time.format('%Y-%m')(new Date(d));
          },
          ticks: 10,
        },
        yAxis: {
          axisLabel: 'Pesos ($)',
          tickFormat: function (d) {
            return '$ ' + d3.format(',.2f')(d);
          },
          axisLabelDistance: 50
        },
        callback: this.certCallBack
      }
    };

    this.g_avance_options = {
      chart: {
        type: 'lineChart',
        height: 450,
        margin: {
          top: 60,
          right: 30,
          bottom: 60,
          left: 80
        },
        x: function (d) { return d.x; },
        y: function (d) { return d.y; },
        showLegend: true,
        duration: 500,
        reduceXticks: false,
        xAxis: {
          axisLabel: 'Periodo',
          tickFormat: function (d) {
            return d3.time.format('%Y-%m')(new Date(d));
          },
          ticks: 10,
        },
        yAxis: {
          axisLabel: 'Avance de obra (%)',
          tickFormat: function (d) {
            return d3.format('.2f')(d) + ' %';
          },
          axisLabelDistance: 20
        },
        forceY: [0],
        callback: this.avanceCallBack
      }
    };


    this.g_costo_options = {
      chart: {
        type: 'multiBarChart',
        height: 450,
        margin: {
          top: 60,
          right: 30,
          bottom: 60,
          left: 120
        },
        x: function (d) { return d.x; },
        y: function (d) { return d.y; },
        stacked: false,
        showLegend: true,
        duration: 500,
        showControls: false,
        reduceXticks: false,
        xAxis: {
          axisLabel: 'Periodo',
          tickFormat: function (d) {
            return d3.time.format('%Y-%m')(new Date(d));
          }
        },
        yAxis: {
          axisLabel: 'Pesos ($)',
          tickFormat: function (d) {
            return '$ ' + d3.format(',.2f')(d);
          },
          axisLabelDistance: 50
        },
        callback: this.costosCallBack
      }
    };


    this.g_consol_options = {
      chart: {
        type: 'lineChart',
        height: 450,
        margin: {
          top: 80,
          right: 30,
          bottom: 60,
          left: 120
        },
        x: function (d) { return d.x; },
        y: function (d) { return d.y; },
        reduceXticks: false,
        xAxis: {
          axisLabel: 'Periodo',
          tickFormat: function (d) {
            return d3.time.format('%Y-%m')(new Date(d));
          },
          ticks: 10,
          // rotateLabels: -45
        },
        yAxis: {
          axisLabel: 'Pesos ($)',
          tickFormat: function (d) {
            return '$ ' + d3.format(',.2f')(d);
          },
          axisLabelDistance: 55
        },
        forceY: [0],
        callback: this.consolidadoCallBack
      }
    };
  }

  setNullGraph() {
    this.graph_data = null;
    this.graph_costo_data = null;
    this.graph_avance_data = null;
    this.graph_consol_data = null;
  }

  showTablero() {
    this.setNullGraph();

    if (this.centro_costo && this.periodo) {
      periodoGlobal = this.periodo;
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

    this._tableroServ.get_graph_certificacion(this.centro_costo, this.periodo).subscribe(
      data => {
        setTimeout(() => this.graph_data = data, 1000);
      },
      error => {
        this.handleError(error);
      }
    );
    this._tableroServ.get_graph_costo(this.centro_costo, this.periodo).subscribe(
      data => {
        setTimeout(() => this.graph_costo_data = data, 1000);
      },
      error => {
        this.handleError(error);
      }
    );
    this._tableroServ.get_graph_avance(this.centro_costo, this.periodo).subscribe(
      data => {
        setTimeout(() => this.graph_avance_data = data, 1000);
      },
      error => {
        this.handleError(error);
      }
    );
    this._tableroServ.get_graph_consolidado(this.centro_costo, this.periodo).subscribe(
      data => {
        this.graph_consol_data = data;
      },
      error => {
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
