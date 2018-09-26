import { ModalService } from './../../../services/core/modal.service';
import { IFamiliaEquipo } from '../../../models/Interfaces';
import { NotificationService } from '../../../services/core/notifications.service';
import { fadeInAnimation } from '../../../_animations/fade-in.animation';
import { TallerService } from '../../../services/taller.service';
import { ActivatedRoute, Router } from '@angular/router';
import { Component, OnInit } from '@angular/core';
import { IEquipo } from '../../../models/Interfaces';

@Component({
  selector: 'app-equipo-detail',
  templateUrl: './equipo-detail.component.html',
  styleUrls: ['./equipo-detail.component.css'],
  animations: [fadeInAnimation]
})
export class EquipoDetailComponent implements OnInit {

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private tallerServ: TallerService,
    private notify_service: NotificationService,
    private modal: ModalService
  ) { }

  equipo: IEquipo = null;
  equipo_id: any;
  familia_equipo: IFamiliaEquipo[] = null;

  initialLoading = true;

  ngOnInit() {
    this.tallerServ.get_familia_equipos().subscribe(
      res => this.familia_equipo = res['results'] as IFamiliaEquipo[],
      error => this.handleError(error)
    );
    this.route.params.subscribe(val => {
      this.equipo_id = val['pk'];
      if (this.equipo_id === 'new') {
        this.equipo = new Object() as IEquipo;
        this.initialLoading = false;
      } else {
        this.refresh_equipo();
      }
    });

  }

  refresh_equipo() {
    this.tallerServ.get_equipo(this.equipo_id).subscribe(
      equipo => {
        this.equipo = equipo;
        this.initialLoading = false;
    });
  }

  create_equipo_modal() {
    this.modal.setUp(
      `Está a punto de añadir un nuevo equipo ¿Continuar?`,
      'Añadir equipo',
      () => this.create_equipo()
    ).open();
  }

  create_equipo() {
    this.tallerServ.create_equipo(this.equipo).subscribe(
      equipo => {
        this.equipo = equipo;
        this.notify_service.success(`Equipo creado correctamente.`);
        this.router.navigate(['/taller', 'equipos', this.equipo.id]);
      },
      error => this.handleError(error)
    );
  }

  save_equipo_modal() {
    this.modal.setUp(
      `¿Guardar los datos del equipo?`,
      'Guardar equipo',
      () => this.save_equipo()
    ).open();
  }

  save_equipo() {
    this.tallerServ.update_equipo(this.equipo).subscribe(
      equipo => {
        this.equipo = equipo;
        this.notify_service.success(`Equipo actualizado correctamente.`);
      },
      error => this.handleError(error)
    );
  }

  set_equipo_baja_modal() {
    this.modal.setUp(
      '¿Desea dar la baja del equipo?',
      'Dar de baja al equipo',
      () => this.dar_la_baja()
    ).open();
  }

  dar_la_baja() {
    this.tallerServ.set_baja_equipos(this.equipo.id).subscribe(
      res => {
        if (res['status'] === 'ok') {
          this.notify_service.success(`Equipo dado de baja.`);
          this.refresh_equipo();
        }
      },
      error => this.handleError(error)
    );
  }

  get can_dar_baja() {
    if (this.equipo.id && !this.equipo.fecha_baja) {
      return true;
    }
    return false;
  }
  handleError(error: any) {
    this.notify_service.error(error._body || error);
  }
}
