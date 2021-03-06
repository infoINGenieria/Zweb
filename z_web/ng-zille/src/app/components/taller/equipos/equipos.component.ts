import { ModalService } from './../../../services/core/modal.service';
import { NotificationService } from '../../../services/core/notifications.service';
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
  f_equipo = '';
  f_estado = '';  // alta o baja
  f_excluir_costos_taller = '';
  f_alquilado = '';
  f_implica_mo_logistica = '';

  page = new Page();

  constructor(
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
    this.tallerServ.get_equipos_list(
      this.page.pageNumber,
      this.f_equipo,
      this.f_estado,
      this.f_excluir_costos_taller,
      this.f_alquilado,
      this.f_implica_mo_logistica
    ).subscribe(
      equipos => {
        this.equipos = equipos['results'] as Array<IEquipo>;
        this.page.pageNumber = this.page.pageNumber;
        this.page.totalElements = Number(equipos.count);
        this.page.totalPages = Math.ceil(this.page.totalElements / this.page.size) || 0;
        this.loaded = true;
      }
    );
  }

  filterList(form: NgForm) {
    console.log(form);
    this.page.pageNumber = 1;
    const { equipo, estado, excluir_costos_taller, alquilado, implica_mo_logistica } = form.value;

    this.f_equipo = equipo;
    this.f_estado = estado;
    this.f_excluir_costos_taller = excluir_costos_taller;
    this.f_alquilado = alquilado;
    this.f_implica_mo_logistica = implica_mo_logistica;
    this.loaded = false;
    this.refresh();
  }

  cleanFilter(form: NgForm) {
    form.reset();
    this.page.pageNumber = 1;
    this.f_equipo = '';
    this.f_estado = '';
    this.f_excluir_costos_taller = '';
    this.f_alquilado = '';
    this.f_implica_mo_logistica = '';
    this.refresh();
  }

  set_equipo_baja_modal(equipo: IEquipo) {
    this.modal.setUp(
      `¿Desea dar la baja del equipo ${equipo.n_interno}?`,
      'Dar de baja al equipo',
      () => {
        this.dar_la_baja(equipo.id);
      }).open();
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
