import { Headers } from '@angular/http';
import { ActivatedRoute, Router } from '@angular/router';
import { Modal } from 'ngx-modialog/plugins/bootstrap/src/ngx-modialog-bootstrap.ng-flat';
import { NotificationService } from '../../../services/core/notifications.service';
import { TallerService } from '../../../services/taller.service';
import { IDatePickerConfig, ECalendarValue } from 'ng2-date-picker';
import { fadeInAnimation } from '../../../_animations/fade-in.animation';
import { Component, OnInit } from '@angular/core';
import { IAsistencia, IEquipo, IRegistroAsistencia, ICentroCosto } from '../../../models/Interfaces';
import { CoreService } from '../../../services/core/core.service';
import { RegistroAsistencia } from '../../../models/RegistroAsistencia';

import * as moment from 'moment';

@Component({
  selector: 'app-asistencia-form',
  templateUrl: './asistencia-form.component.html',
  styleUrls: ['./asistencia-form.component.css'],
  animations: [fadeInAnimation]
})
export class AsistenciaFormComponent implements OnInit {

  asistencia: IAsistencia = null;
  equipos: IEquipo[] = [];
  centros_costos: ICentroCosto[] = [];

  asistencia_pk: any;

  initialLoading = true;

  is_cloning = false;

  constructor(
    private tallerServ: TallerService,
    private coreServ: CoreService,
    private notify_service: NotificationService,
    private modal: Modal,
    private route: ActivatedRoute,
    private router: Router,
  ) { }

  datePickerConfig: IDatePickerConfig = {
    'format': 'DD/MM/YYYY',
    'drops': 'down',
    'locale': 'es',
    'returnedValueType': ECalendarValue.String
  };

  ngOnInit() {

    // equipos
    this.tallerServ.get_equipos_activos_list().subscribe(
      equipos => {
        this.equipos = equipos['equipos'] as IEquipo[];
        this.route.params.subscribe(val => {
          this.asistencia_pk = val['pk'];
          if (val['clone']) {
            this.is_cloning = true;
          }
          if (this.asistencia_pk === 'new') {
            this.newAsistenciaAndfillRegistros()
            this.initialLoading = false;
          } else {
            this.refresh();
          }
        });
      },
      error => this.handleError(error)
    );

    // centros de costos
    this.coreServ.get_centro_costos_list().subscribe(
      cc => this.centros_costos = cc as ICentroCosto[],
      error => this.handleError(error)
    );
  }

  newAsistenciaAndfillRegistros() {
    // traer ultimo registro
    this.asistencia = new Object() as IAsistencia;
    this.asistencia.registros = [];
    this.asistencia.dia =  moment().format('DD/MM/YYYY');
    for (const eq of this.equipos) {
      const registro = new RegistroAsistencia();
      registro.equipo = eq;
      registro.equipo_id = eq.id;
      this.asistencia.registros.push(registro);
    }
  }

  trackByIndex(index: number, item: RegistroAsistencia) {
    return index;
  }

  get is_valid(): boolean {
    if (this.has_all_selected && this.asistencia.dia) {
      return true;
    }
    return false;
  }

  get has_all_selected(): boolean {
    const valid = this.asistencia.registros.filter(reg => !reg.centro_costo_id ).length === 0;
    return valid;
  }

  handler_error_guardado(err) {
    console.error(err);
    try {
      const msg = JSON.parse(err._body);
      if (msg.dia) {
        this.notify_service.warning('Ya existe asistencia para el día seleccionado. Debe seleccionar otra fecha');
      } else {
        this.notify_service.error('Un error ha ocurrido. Intente nuevamente.')
      }
    } catch (ex) {
      this.handleError(err);
    }
  }

  handler_success_guardado(asist, created) {
    this.asistencia = asist;
    if (created) {
      this.notify_service.success(`Asistencia creada correctamente.`);
      this.router.navigate(['/taller', 'asistencia']);
    } else {
      this.notify_service.success(`Asistencia guardada correctamente.`);
    }
  }
  guardar_asistencia() {
    if (this.asistencia.pk) {
      this.tallerServ.update_asistencia(this.asistencia).subscribe(
        asist => this.handler_success_guardado(asist, false),
        err => this.handler_error_guardado(err)
      );
    } else {
      this.tallerServ.create_asistencia(this.asistencia).subscribe(
        asist => this.handler_success_guardado(asist, true),
        err => this.handler_error_guardado(err)
      );
    }
  }

  clonar_asistencia() {
    this.asistencia.pk = null;
    this.tallerServ.create_asistencia(this.asistencia).subscribe(
      asist => this.handler_success_guardado(asist, true),
      err => this.handler_error_guardado(err)
    );
  }

  guardar_asistencia_modal() {
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title(`Asistencia de ${this.asistencia.dia}`)
    .message(`¿Desea guardar la asistencia?`)
    .cancelBtn('Cancelar')
    .okBtn('Guardar')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => this.guardar_asistencia(),
          () => {}
        );
      },
    );
  }

  clonar_asistencia_modal() {
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title(`Asistencia de ${this.asistencia.dia}`)
    .message(`Está creando una nueva asistencia a partir de la seleccionada. ¿Desea continuar?`)
    .cancelBtn('Cancelar')
    .okBtn('Si, guardar!')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => this.clonar_asistencia(),
          () => {}
        );
      },
    );
  }
  refresh() {
    this.tallerServ.get_asistencia(this.asistencia_pk).subscribe(
      asistencia => {
        this.asistencia = asistencia;
        this.initialLoading = false;
    });
  }

  handleError(error: any) {
    this.notify_service.error(error._body || error);
  }

}
