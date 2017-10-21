import { NgForm } from '@angular/forms';
import { CoreService } from './../../services/core/core.service';
import { NotificationService } from './../../services/core/notifications.service';
import { Modal } from 'ngx-modialog/plugins/bootstrap';
import { ICertificacion, ICentroCosto, IPeriodo } from './../../models/Interfaces';
import { RegistroService } from './../../services/registro/registro.service';
import { Component, OnInit } from '@angular/core';
import { fadeInAnimation } from './../../_animations/fade-in.animation';

@Component({
  selector: 'app-certificaciones-proyeccion',
  templateUrl: './certificaciones-proyeccion.component.html',
  animations: [fadeInAnimation]
})
export class CertificacionesProyeccionComponent implements OnInit {

  certificaciones: ICertificacion[] = [];
  centro_costos: ICentroCosto[] = [];
  periodos: IPeriodo[] = [];
  loaded = false;

  constructor(
    private registroServ: RegistroService,
    private core_serv: CoreService,
    private _notifications: NotificationService,
    private _modal: Modal
  ) { }

  refresh() {
    this.loaded = false;
    this.registroServ.get_certificacion_proyeccion_list().subscribe(
      certs => {
        this.certificaciones = certs as ICertificacion[];
      },
      error => this.handleError(error),
      () => this.loaded = true
    );
  }

  ngOnInit() {
    this.refresh();
    this.core_serv.get_centro_costos_list().subscribe(cc => {
      this.centro_costos = cc as ICentroCosto[];
    }, error => this.handleError(error));
    this.core_serv.get_periodos_list().subscribe(p => {
      this.periodos = p as IPeriodo[];
    }, error => this.handleError(error));
  }

  handleError(error: any) {
    this._notifications.error(error);
  }

  filterList(form: NgForm) {
    const { centro_costo, periodo } = form.value;
    this.loaded = false;
    this.registroServ.get_certificacion_proyeccion_list(centro_costo, periodo).subscribe(certificaciones => {
      this.certificaciones = certificaciones as ICertificacion[];
      this.loaded = true;
    }, error => this.handleError(error));
  }

  delete(cert: ICertificacion) {
    const dialogRef = this._modal.confirm()
    .showClose(true)
    .title('Confirmación de eliminación')
    .message(
      '¿Está seguro que desea <b>eliminar</b> esta proyección ' +
      'de certificación del sistema?<br><b>Esta acción no puede deshacerse.</b>')
    .cancelBtn('Cancelar')
    .okBtn('Eliminar')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => {
            this.registroServ.delete_certificacion_proyeccion(cert).subscribe(
              r => {
                this.refresh();
                this._notifications.success('Proyección de Certificación eliminada correctamente.');
              },
              error => this.handleError(error));
          },
          () => {}
        );
      },
    );
  }

}
