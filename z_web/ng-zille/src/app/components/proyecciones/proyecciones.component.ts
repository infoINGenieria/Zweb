import { NotificationService } from '../../services/core/notifications.service';
import { ICentroCosto } from '../../models/Interfaces';
import { Component, OnInit } from '@angular/core';
import { fadeInAnimation } from '../../_animations/fade-in.animation';
import { CoreService } from '../../services/core/core.service';

@Component({
  selector: 'app-proyecciones',
  templateUrl: './proyecciones.component.html',
  styleUrls: ['./proyecciones.component.css'],
  animations: [fadeInAnimation]
})
export class ProyeccionesComponent implements OnInit {

  centro_costos: ICentroCosto[] = [];
  loaded = false;

  constructor(
    private core_serv: CoreService,
    private _notifications: NotificationService,
  ) {
  }

  ngOnInit() {
    this.refresh();
  }

  refresh() {
    this.loaded = false;
    this.core_serv.get_centro_costos_list().subscribe(cc => {
      this.centro_costos = cc as ICentroCosto[];
      this.loaded = true;
    }, error => this.handleError(error));
  }

  handleError(error: any) {
    console.error(error);
    this._notifications.error(error._body || error);
  }




}
