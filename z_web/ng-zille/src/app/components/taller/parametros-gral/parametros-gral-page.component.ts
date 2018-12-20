import { fadeInAnimation } from './../../../_animations/fade-in.animation';
import { ModalService } from './../../../services/core/modal.service';
import { IParametrosGenerales, IPeriodo } from './../../../models/Interfaces';
import { NotificationService } from './../../../services/core/notifications.service';
import { TallerService } from './../../../services/taller.service';
import { ActivatedRoute, Router } from '@angular/router';
import { Component, OnInit } from '@angular/core';
import { CoreService } from '../../../services/core/core.service';

@Component({
  selector: 'app-parametros-gral-page',
  templateUrl: './parametros-gral-page.component.html',
  styleUrls: ['./parametros-gral-page.component.css'],
  animations: [fadeInAnimation]
})
export class ParametrosGralPageComponent implements OnInit {

  initialLoading = true;

  parametro_general: IParametrosGenerales = null;
  parametro_general_id: any;
  periodos: IPeriodo[] = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private tallerServ: TallerService,
    private coreServ: CoreService,
    private notify_service: NotificationService,
    public modal: ModalService
  ) { }

  ngOnInit() {
    this.coreServ.get_periodos_list().subscribe(
      res => this.periodos = res,
      error => this.handleError(error)
    );
    this.route.params.subscribe(val => {
      this.parametro_general_id = val['pk'];
      if (this.parametro_general_id === 'new') {
        this.tallerServ.get_parametros_generales_latest().subscribe(
          res => {
            this.parametro_general = res as IParametrosGenerales;
            this.parametro_general.pk = null;
            this.parametro_general.valido_desde = null;
            this.parametro_general.valido_desde_id = null;
            this.initialLoading = false;
          },
          err => {
            console.log(err);
            this.parametro_general = new Object() as IParametrosGenerales;
            this.initialLoading = false;
          }
        )
      } else {
        this.refresh_parametro();
      }
    });

  }

  refresh_parametro() {
    this.tallerServ.get_parametros_generales(this.parametro_general_id).subscribe(
      parametro_general => {
        this.parametro_general = parametro_general;
        this.initialLoading = false;
    });
  }

  create_parametro_general_modal() {
    this.modal.setUp(
      'Está a punto de añadir un nuevo conjunto de parámetros generales ¿Continuar?',
      'Añadir parámetros generales',
      () => this.create_parametro_general()
    ).open();
  }

  create_parametro_general() {
    this.tallerServ.create_parametros_generales(this.parametro_general).subscribe(
      parametro_general => {
        this.parametro_general = parametro_general;
        this.notify_service.success(`Parametros generales creados correctamente.`);
        this.router.navigate(['/taller', 'parametros', 'general', this.parametro_general.pk]);
      },
      error => this.handleError(error)
    );
  }

  save_parametro_general_modal() {
    this.modal.setUp(
      '¿Guardar los datos del conjunto de parámetros generales?',
      'Guardar parámetros generales',
      () => this.save_parametro_general()
    ).open();
  }

  save_parametro_general() {
    this.tallerServ.update_parametros_generales(this.parametro_general).subscribe(
      parametro_general => {
        this.parametro_general = parametro_general;
        this.notify_service.success(`Parámetros generales actualizado correctamente.`);
      },
      error => this.handleError(error)
    );
  }

  handleError(error: any) {
    this.notify_service.error(error._body || error);
  }
}
