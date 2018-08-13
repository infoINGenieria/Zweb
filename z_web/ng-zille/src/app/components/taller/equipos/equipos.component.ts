import { NotificationService } from '../../../services/core/notifications.service';
import { Modal } from 'ngx-modialog/plugins/bootstrap/src/ngx-modialog-bootstrap.ng-flat';
import { Page } from '../../../models/Page';
import { NgForm } from '@angular/forms';
import { fadeInAnimation } from '../../../_animations/fade-in.animation';
import { IEquipo } from '../../../models/Interfaces';
import { TallerService } from '../../../services/taller.service';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-equipos',
  templateUrl: './equipos.component.html',
  styleUrls: ['./equipos.component.css'],
  animations: [fadeInAnimation]
})
export class EquiposComponent implements OnInit {

  equipos: Array<IEquipo> = [];
  loaded = false;

  // filter
  f_ninterno = '';
  f_marca = '';
  f_modelo = '';
  f_tipo = '';
  f_dominio = '';
  f_anio = '';
  f_estado = '';  // alta o baja


  page = new Page();

  constructor(
    private tallerServ: TallerService,
    private notify_service: NotificationService,
    private modal: Modal
  ) { }

  ngOnInit() {
    this.refresh();

  }

  refresh(newPage?) {
    if (newPage) {
      this.page.pageNumber = newPage;
    }
    this.loaded = false;
    this.tallerServ.get_equipos_list(
      this.page.pageNumber,
      this.f_ninterno,
      this.f_marca,
      this.f_modelo,
      this.f_tipo,
      this.f_dominio,
      this.f_anio,
      this.f_estado
    ).subscribe(
      equipos => {
        this.equipos = equipos['results'] as Array<IEquipo>;
        this.page.pageNumber = this.page.pageNumber;
        this.page.totalElements = Number.parseInt(equipos.count);
        this.page.totalPages = Math.ceil(this.page.totalElements / this.page.size) || 0;
        this.loaded = true;
      }
    );
  }

  filterList(form: NgForm) {
    console.log(form);
    this.page.pageNumber = 1;
    const { ninterno, marca, modelo, tipo, dominio, anio, estado } = form.value;

    this.f_ninterno = ninterno;
    this.f_marca = marca;
    this.f_modelo = modelo;
    this.f_tipo = tipo;
    this.f_dominio = dominio;
    this.f_anio = anio;
    this.f_estado = estado;
    this.loaded = false;
    this.refresh();
  }

  cleanFilter(form: NgForm) {
    form.reset();
    this.page.pageNumber = 1;
    this.f_ninterno = '';
    this.f_marca = '';
    this.f_modelo = '';
    this.f_tipo = '';
    this.f_dominio = '';
    this.f_anio = '';
    this.f_estado = '';
    this.refresh();
  }

  set_equipo_baja_modal(equipo: IEquipo) {
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Dar de baja al equipo')
    .message(`¿Desea dar la baja del equipo ${equipo.n_interno}?`)
    .cancelBtn('Cancelar')
    .okBtn('Si, continuar!')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => this.dar_la_baja(equipo.id),
          () => {}
        );
      },
    );
  }

  dar_la_baja(pk) {
    this.tallerServ.set_baja_equipos(pk).subscribe(
      res => {
        if (res['status'] === 'ok') {
          this.notify_service.success(`Equipo dado de baja.`);
          let equipo = this.equipos.find(eq => eq.id === pk);
          equipo.fecha_baja = res['equipo'].fecha_baja;
        }
      },
      error => this.handleError(error)
    );
  }
  can_dar_baja(eq) {
    if (eq.id && !eq.fecha_baja) {
      return true;
    }
    return false;
  }

  handleError(error: any) {
    this.notify_service.error(error._body || error);
  }
}
