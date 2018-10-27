import { ModalService } from './../../../services/core/modal.service';
import { fadeInAnimation } from '../../../_animations/fade-in.animation';
import { NgForm } from '@angular/forms';
import { NotificationService } from '../../../services/core/notifications.service';
import { TallerService } from '../../../services/taller.service';
import { Page } from '../../../models/Page';
import { IAsistencia } from '../../../models/Interfaces';
import { IDatePickerConfig } from 'ng2-date-picker';
import { Component, OnInit } from '@angular/core';
import { CoreService } from '../../../services/core/core.service';

import * as moment from 'moment';

@Component({
  selector: 'app-asistencias',
  templateUrl: './asistencias.component.html',
  styleUrls: ['./asistencias.component.css'],
  animations: [fadeInAnimation]
})
export class AsistenciasComponent implements OnInit {

  asistencias: IAsistencia[] = [];

  loaded = false;

  // filter
  f_desde = '';
  f_hasta = '';

  page = new Page();

  datePickerConfig: IDatePickerConfig = {
    'format': 'DD/MM/YYYY',
    'drops': 'down',
    'locale': 'es'
  };

  constructor(
    private coreServ: CoreService,
    private tallerServ: TallerService,
    private notify_service: NotificationService,
    private modal: ModalService
  ) { }

  ngOnInit() {
    this.refresh();

  }

  refresh(newPage?) {
    if (newPage) {
      this.page.pageNumber = newPage;
    }
    this.loaded = false;
    this.tallerServ.get_asistencias_list(
      this.page.pageNumber,
      this.f_desde,
      this.f_hasta,
    ).subscribe(
      asistencias => {
        this.asistencias = asistencias['results'] as Array<IAsistencia>;
        this.page.pageNumber = this.page.pageNumber;
        this.page.totalElements = Number.parseInt(asistencias.count);
        this.page.totalPages = Math.ceil(this.page.totalElements / this.page.size);
        this.loaded = true;
      }
    );
  }

  filterList(form: NgForm) {
    console.log(form);
    this.page.pageNumber = 1;
    const { desde, hasta } = form.value;

    this.f_desde = desde;
    this.f_hasta = hasta;
    this.loaded = false;
    this.refresh();
  }

  cleanFilter(form: NgForm) {
    form.reset();
    this.page.pageNumber = 1;
    this.f_desde = '';
    this.f_hasta = '';
    this.refresh();
  }

  handleError(error: any) {
    this.notify_service.error(error._body || error);
  }

  get_moment_day(dia) {
    return moment(dia, 'DD/MM/YYYY');
  }

  get_nombre(dia) {
    return this.get_moment_day(dia).format('dddd');
  }

  isWeekend(asistencia) {
    const day = this.get_moment_day(asistencia.dia);
    if (day.weekday() === 5 || day.weekday() === 6) {
      return true;
    }
    return false;
  }

  eliminar_asistencia(asistencia: IAsistencia) {
    this.tallerServ.delete_asistencia(asistencia).subscribe(
      asist => {
        this.notify_service.success('Assitencia eliminada correctamente.');
        this.refresh();
      },
      err => {
        this.handleError(err);
      }
    );
  }

  guardar_asistencia_modal(asistencia: IAsistencia) {
    this.modal.setUp(
      `¿Desea eliminar la asistencia del día ${asistencia.dia}?`,
      `¡¡Eliminar asistencia!!`,
      () => this.eliminar_asistencia(asistencia)
    ).open();
  }
}
