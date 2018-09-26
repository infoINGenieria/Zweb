import { NgForm } from '@angular/forms';
import { CoreService } from '../../services/core/core.service';
import { NotificationService } from '../../services/core/notifications.service';
import { ICertificacion, ICentroCosto, IPeriodo } from '../../models/Interfaces';
import { RegistroService } from '../../services/registro/registro.service';
import { Component, OnInit } from '@angular/core';
import { fadeInAnimation } from '../../_animations/fade-in.animation';
import { ModalService } from '../../services/core/modal.service';

@Component({
  selector: 'app-certificaciones-real',
  templateUrl: './certificaciones-real.component.html',
  animations: [fadeInAnimation]
})
export class CertificacionesRealComponent implements OnInit {

  certificaciones: ICertificacion[] = [];
  centro_costos: ICentroCosto[] = [];
  periodos: IPeriodo[] = [];
  loaded = false;

  selectedCertificacion: ICertificacion;

  constructor(
    private registroServ: RegistroService,
    private core_serv: CoreService,
    private _notifications: NotificationService,
    public modal: ModalService
  ) { }

  refresh() {
    this.loaded = false;
    this.registroServ.get_certificacion_list().subscribe(
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
    this._notifications.error(error._body || error);
  }

  filterList(form: NgForm) {
    const { centro_costo, periodo } = form.value;
    this.loaded = false;
    this.registroServ.get_certificacion_list(centro_costo, periodo).subscribe(certificaciones => {
      this.certificaciones = certificaciones as ICertificacion[];
      this.loaded = true;
    }, error => this.handleError(error));
  }

  delete(cert: ICertificacion) {
    this.selectedCertificacion = cert;
    this.modal.setUp(
      '¿Está seguro que desea <b>eliminar</b> esta certificación del sistema?',
      'Confirmación de eliminación',
      () => this.delete_certificacion()
    ).open();
  }

  delete_certificacion() {
    this.registroServ.delete_certificacion(this.selectedCertificacion).subscribe(
      r => {
        this.refresh();
        this._notifications.success('Certificación eliminada correctamente.');
      },
      error => this.handleError(error));
  }

}
