import { TableroService } from './../../services/tablero.service';
import { NotificationService } from './../../services/core/notifications.service';
import { ICentroCosto, IPeriodo } from './../../models/Interfaces';
import { CoreService } from './../../services/core/core.service';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-tablero-control-os',
  templateUrl: './tablero-control-os.component.html',
  styleUrls: ['./tablero-control-os.component.css']
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
  }

  showTablero() {
    if (this.centro_costo && this.periodo) {
      this._tableroServ.get_data_table(this.centro_costo, this.periodo).subscribe(
        data => this.data = data
      );
    } else {
      this._notifications.warning('Debe seleccionar un proyecto y el periodo.')
    }
  }

  get_items_costos(): String[] {
    let keys = Object.keys(this.data['costos']['acumulado']);
    keys.splice(keys.indexOf('subtotal'));
    keys.splice(keys.indexOf('total_costos'));
    return keys;
  }

  handleError(error: any) {
    this._notifications.error(error._body || error);
  }
}
