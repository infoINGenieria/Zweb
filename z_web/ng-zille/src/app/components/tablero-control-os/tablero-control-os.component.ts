import { Modal } from 'ngx-modialog/plugins/bootstrap';
import {
  TableroService
} from './../../services/tablero.service';
import {
  NotificationService
} from './../../services/core/notifications.service';
import {
  ICentroCosto,
  IPeriodo,
  ITableroControlEmitido
} from './../../models/Interfaces';
import {
  CoreService
} from './../../services/core/core.service';
import {
  Component,
  OnInit,
  ViewEncapsulation
} from '@angular/core';

import * as moment from 'moment';

import { saveSvgAsPng, svgAsPngUri } from 'save-svg-as-png';

declare let d3: any;

let periodoGlobal: IPeriodo;

@Component({
  selector: 'app-tablero-control-os',
  templateUrl: './tablero-control-os.component.html',
  styleUrls: ['./tablero-control-os.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class TableroControlOsComponent implements OnInit {

  showing_data = false;
  is_freeze = false;
  pdf: string = null;
  emitido_el: string = null;

  periodos: IPeriodo[] = [];
  periodo: IPeriodo;
  centro_costos: ICentroCosto[] = [];
  centro_costo: ICentroCosto;

  data: any = null;
  info_obra: any = null;
  revisiones_historico: any = null;

  tablero: ITableroControlEmitido;

  // feo pero funciona. Estos haeders sirven para iterar en cada subconjunto
  headers = ['acumulado', 'faltante_estimado', 'faltante_presupuesto',
    'estimado', 'presupuesto', 'comercial'
  ];


  g_cert_options = null;
  graph_data = null;

  g_costo_options = null;
  graph_costo_data = null;

  g_avance_options = null;
  graph_avance_data = null;

  g_consol_options = null;
  graph_consol_data = null;

  images_count = 0;

  constructor(
    private _coreServ: CoreService,
    private _tableroServ: TableroService,
    private _notifications: NotificationService,
    private _modal: Modal
  ) {}

  certCallBack(chart) {
    setTimeout(function () {
      // drawing the line
      const fecha = moment(periodoGlobal.fecha_fin, 'DD/MM/YYYY').add(1, 'months').startOf('month');
      const limit = fecha.toDate().getTime();
      const xgrid = [limit];
      if (!chart.container) {
        return;
      }

      const max_value = d3.max([
        d3.max(chart.container.__data__[0].values, function (d) {
          return d.y;
        }),
        d3.max(chart.container.__data__[1].values, function (d) {
          return d.y;
        })
      ]);
      let custLine = d3.select('#nvd3-graph-cert')
        .select('.nv-multibar')
        .append('g');

      custLine.selectAll('line')
        .data(xgrid)
        .enter()
        .append('line')
        .attr({
          x1: function (d) {
            return chart.xAxis.scale()(d);
          },
          y1: function (d) {
            return chart.yAxis.scale()(0);
          },
          x2: function (d) {
            return chart.xAxis.scale()(d);
          },
          y2: function (d) {
            return chart.yAxis.scale()(max_value);
          }
        })
        .style('stroke', '#FF0000')
        .style('stroke-dasharray', '5,5')
        .style('stroke-width', '2px');

      // resize the chart with vertical lines
      // but only the third line will be scaled properly...
      nv.utils.windowResize(function () {
        chart.update();
        custLine.selectAll('line')
          .transition()
          .attr({
            x1: function (d) {
              return chart.xAxis.scale()(d);
            },
            y1: function (d) {
              return chart.yAxis.scale()(0);
            },
            x2: function (d) {
              return chart.xAxis.scale()(d);
            },
            y2: function (d) {
              return chart.yAxis.scale()(max_value);
            }
          });
      });
    }, 500);
  }

  avanceCallBack(chart) {
    setTimeout(function () {
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
          x1: function (d) {
            return chart.xAxis.scale()(d);
          },
          y1: function (d) {
            return chart.yAxis.scale()(0);
          },
          x2: function (d) {
            return chart.xAxis.scale()(d);
          },
          y2: function (d) {
            return chart.yAxis.scale()(100);
          }
        })
        .style('stroke', '#FF0000')
        .style('stroke-dasharray', '5,5')
        .style('stroke-width', '2px');

      chart.xScale(d3.time.scale());
      chart.update();

      // resize the chart with vertical lines
      // but only the third line will be scaled properly...
      nv.utils.windowResize(function () {
        chart.update();
        custLine.selectAll('line')
          .transition()
          .attr({
            x1: function (d) {
              return chart.xAxis.scale()(d);
            },
            y1: function (d) {
              return chart.yAxis.scale()(0);
            },
            x2: function (d) {
              return chart.xAxis.scale()(d);
            },
            y2: function (d) {
              return chart.yAxis.scale()(100);
            }
          });
      });
    }, 500);
  }

  costosCallBack(chart) {
    setTimeout(function () {
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
        d3.max(chart.container.__data__[0].values, function (d) {
          return d.y;
        }),
        d3.max(chart.container.__data__[1].values, function (d) {
          return d.y;
        })
      ]);

      custLine.selectAll('line')
        .data(xgrid)
        .enter()
        .append('line')
        .attr({
          x1: function (d) {
            return chart.xAxis.scale()(d);
          },
          y1: function (d) {
            return chart.yAxis.scale()(0);
          },
          x2: function (d) {
            return chart.xAxis.scale()(d);
          },
          y2: function (d) {
            return chart.yAxis.scale()(max_value);
          }
        })
        .style('stroke', '#FF0000')
        .style('stroke-dasharray', '5,5')
        .style('stroke-width', '2px');

      // resize the chart with vertical lines
      // but only the third line will be scaled properly...
      nv.utils.windowResize(function () {
        chart.update();
        custLine.selectAll('line')
          .transition()
          .attr({
            x1: function (d) {
              return chart.xAxis.scale()(d);
            },
            y1: function (d) {
              return chart.yAxis.scale()(0);
            },
            x2: function (d) {
              return chart.xAxis.scale()(d);
            },
            y2: function (d) {
              return chart.yAxis.scale()(max_value);
            }
          });
      });
    }, 500);
  }

  consolidadoCallBack(chart) {
    setTimeout(function () {
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
        d3.max(dataset[0].values, function (d) {
          return d.y;
        }),
        d3.max(dataset[1].values, function (d) {
          return d.y;
        })
      ]);

      custLine.selectAll('line')
        .data(xgrid)
        .enter()
        .append('line')
        .attr({
          x1: function (d) {
            return chart.xAxis.scale()(d);
          },
          y1: function (d) {
            return chart.yAxis.scale()(0);
          },
          x2: function (d) {
            return chart.xAxis.scale()(d);
          },
          y2: function (d) {
            return chart.yAxis.scale()(max_value);
          }
        })
        .style('stroke', '#FF0000')
        .style('stroke-dasharray', '5,5')
        .style('stroke-width', '2px');

      // resize the chart with vertical lines
      // but only the third line will be scaled properly...
      nv.utils.windowResize(function () {
        chart.update();
        custLine.selectAll('line')
          .transition()
          .attr({
            x1: function (d) {
              return chart.xAxis.scale()(d);
            },
            y1: function (d) {
              return chart.yAxis.scale()(0);
            },
            x2: function (d) {
              return chart.xAxis.scale()(d);
            },
            y2: function (d) {
              return chart.yAxis.scale()(max_value);
            }
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
        x: function (d) {
          return d.x;
        },
        y: function (d) {
          return d.y;
        },
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
        x: function (d) {
          return d.x;
        },
        y: function (d) {
          return d.y;
        },
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
        x: function (d) {
          return d.x;
        },
        y: function (d) {
          return d.y;
        },
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
        x: function (d) {
          return d.x;
        },
        y: function (d) {
          return d.y;
        },
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

  cerrarTablero() {
    this.showing_data = false;
    this.setNullGraph();
    this.data = null;
    this.is_freeze = false;
    this.pdf = null;
    this.emitido_el = null;
  }

  showTablero() {
    this.setNullGraph();

    this.tablero = new Object as ITableroControlEmitido;

    if (this.centro_costo && this.periodo) {
      periodoGlobal = this.periodo;
      this.tablero.obra = this.centro_costo;
      this.tablero.periodo = this.periodo;
      this._tableroServ.get_data_table(this.centro_costo, this.periodo).subscribe(
        data => {
          this.data = data;
          try {
            if (data['is_freeze']) {
              this.is_freeze = true;
              this.pdf = data['pdf'];
              this.emitido_el = data['emitido'];
              this.info_obra = data['info_obra'];
              this.revisiones_historico = data['revisiones_historico'];
            } else {
              this.info_obra = this.centro_costo.info_obra;
              this.revisiones_historico = this.data['revisiones_historico'];
            }
          } catch (e) {
            this.info_obra = this.centro_costo.info_obra;
            this.revisiones_historico = this.data['revisiones_historico'];
          }
          this.get_data_graphs();
          setTimeout(() => this.showing_data = true, 500);
        },
        error => {
          this.data = null;
          this.showing_data = false;
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
    return this.data['costos_keys'];
  }

  handleError(error: any) {
    try {
      const _error = JSON.parse(error._body);
      this._notifications.error(_error.detail);
    } catch (ex) {
      this._notifications.error(error._body || error);
    }
  }

  printTablero(comentarios?: string) {
    this._notifications.info('Emitiendo el tablero, por favor, espere...');
    this.tablero.comentario = comentarios;
    setTimeout(() => {
      const ts = moment();
      while (this.images_count < 4 ) {
        const paso = moment().diff(ts, 'seconds');
        if (paso > 5) {
          this._notifications.error('Error al emitir el reporte. Intente nuevamente.');
          return;
        }
       }
      this._tableroServ.emitir_tablero(this.tablero).subscribe(
        r => {
          this.showTablero();
          this._notifications.success('Tablero emitido correctamente.');
        },
        e => {
          this.handleError(e);
        }
      );
    }, 500);
  }

  printTableroPrompt() {
    this.images_count = 0;
    const dialogRef = this._modal.prompt()
      .showClose(true)
      .title('Confirmación de emisión de tablero')
      .message(`
        <h4>Emisión de tablero</h4>
        <strong>¡Atención! Esta acción no puede deshacerse.</strong>
        <p>Al emitir el tablero, el mismo pasa a estar en sólo lectura, ignorando cualquier cambio
        que se haga sobre las proyecciones y demás datos intervinietes para
        ${this.centro_costo.obra}, periodo ${this.periodo.descripcion}.</p><br>
        <p>A continuación puede añadir un comentario sobre el mismo que desee incluir en el tablero (opcional):</p>
      `)
      .cancelBtn('Cancelar')
      .okBtn('Emitir')
      .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => {
            this.printTablero(result);
          },
          () => {}
        );
      },
    );

    this.tablero.obra_id = this.centro_costo.id;
    this.tablero.periodo_id = this.periodo.pk;
    this.tablero.tablero_data = JSON.stringify(this.data);
    this.tablero.consolidado_data = JSON.stringify(this.graph_consol_data);
    this.tablero.certificacion_data = JSON.stringify(this.graph_data);
    this.tablero.costos_data = JSON.stringify(this.graph_costo_data);
    this.tablero.avance_data = JSON.stringify(this.graph_avance_data);
    this.tablero.info_obra = JSON.stringify(this.info_obra);
    this.tablero.revisiones_historico = JSON.stringify(this.revisiones_historico);
    this.tablero.resultados_data = '';

    // Get the d3js SVG element
    let tmp  = document.getElementById('nvd3-graph-avance');
    let svg = tmp.getElementsByTagName('svg')[0];
    svgAsPngUri(svg, {scale: 1.2}, uri => {
      this.tablero.avance_img = uri;
      this.images_count++;
    });

    tmp  = document.getElementById('nvd3-graph-consolidado');
    svg = tmp.getElementsByTagName('svg')[0];
    svgAsPngUri(svg, {scale: 1.2}, uri => {
      this.tablero.consolidado_img = uri;
      this.images_count++;
    });

    tmp  = document.getElementById('nvd3-graph-cert');
    svg = tmp.getElementsByTagName('svg')[0];
    svgAsPngUri(svg, {scale: 1.2}, uri => {
      this.tablero.certificacion_img = uri;
      this.images_count++;
    });

    tmp  = document.getElementById('nvd3-graph-costo');
    svg = tmp.getElementsByTagName('svg')[0];
    svgAsPngUri(svg, {scale: 1.2}, uri => {
      this.tablero.costos_img = uri;
      this.images_count++;
    });

    const table = document.getElementById('resultado');
    this.tablero.tablero_html = table.outerHTML;

  }
}
