import { NotificationService } from './../../services/core/notifications.service';
import { Certificacion } from './../../models/Certificacion';
import { MyCurrencyFormatterDirective } from './../../directives/currency-formatter.directive';
import { MyCurrencyPipe } from './../../pipes/my-currency.pipe';
import { ICertificacion, ICentroCosto, IPeriodo, ICertificacionItem } from './../../models/Interfaces';
import { RegistroService } from './../../services/registro/registro.service';
import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute} from '@angular/router';
import { CoreService } from '../../services/core/core.service';
import { fadeInAnimation } from '../../_animations/index';
import { Modal } from 'ngx-modialog/plugins/bootstrap';

@Component({
  selector: 'app-certificaciones',
  templateUrl: './certificaciones.component.html',
  styleUrls: ['./certificaciones.component.css'],
  animations: [fadeInAnimation],
})
export class CertificacionesComponent implements OnInit {
  centro_costo: ICentroCosto;
  certificaciones: ICertificacion[];
  real_certificaciones: ICertificacion[];
  periodos: IPeriodo[];

  isDisabled = false;

  constructor(
    private route: ActivatedRoute,
    private registro_service: RegistroService,
    private core_service: CoreService,
    private _notifications: NotificationService,
    private modal: Modal
  ) { }

  ngOnInit() {
    this.route.params.subscribe(val => {
      const obra_id = val['obra_id'];
      this.core_service.get_centro_costos(obra_id).subscribe(cc => this.centro_costo = cc);
      this.core_service.get_periodos_list().subscribe(periodos => this.periodos = periodos);
      this.registro_service
        .get_certificacion_proyeccion_by_obra(obra_id)
        .subscribe(certs => this.certificaciones = certs);
      this.registro_service
        .get_certificacion_real_by_obra(obra_id)
        .subscribe(certs => this.real_certificaciones = certs);
    });
  }

  refresh() {
    this.registro_service
      .get_certificacion_proyeccion_by_obra(this.centro_costo.id)
      .subscribe(certs => this.certificaciones = certs);
    this.registro_service
      .get_certificacion_real_by_obra(this.centro_costo.id)
      .subscribe(certs => this.real_certificaciones = certs);
  }

  trackByIndex(index: number, item: ICertificacionItem) {
    return index;
  }

  itemIsValid(item: ICertificacion): boolean {
    if (item.periodo_id) {
      if (this._tonum(item.items[0].monto) > 0) {
        return true;
      }
    return false;
    }
  }

  isAllValid() {
    let periodos = [];
    for (let cert of this.certificaciones) {
      const id = this._tonum(cert.periodo_id)
      if (periodos.indexOf(id) !== -1) {
        return false;
      }
      periodos.push(id);
    }
    return true;
  }

  find_real(item: ICertificacion) {
    if (this.real_certificaciones) {
      return this.real_certificaciones.find((i) => {
        return i.periodo_id === item.periodo_id;
      });
    }
  }

  acumulado(item: ICertificacion): number {
    const posicion = this.certificaciones.indexOf(item);
    let acumulado = 0.0;
    for (const cert of this.certificaciones.slice(0, posicion + 1)) {
      acumulado += this._tonum(cert.items[0].monto);
    }
    return acumulado;
  }


  acumuladoConsolidado(item: ICertificacion): number {
    /*
      Suma acumulado de los datos reales y, cuando estos no existan,
      la proyección del mes correspondiente.
    */
    const posicion = this.certificaciones.indexOf(item);
    let acumulado = 0.0;
    for (const cert of this.certificaciones.slice(0, posicion + 1)) {
      let real = this.find_real(cert);
      if (real) {
        acumulado += this._tonum(real.total);
      } else {
        acumulado += this._tonum(cert.items[0].monto);
      }
    }
    return acumulado;
  }

  aniadirCertificacion() {
    let item = new Object as ICertificacionItem;
    item.monto = 0;
    let certificacion = new Certificacion();
    certificacion.items = Array<ICertificacionItem>();
    certificacion.items.push(item);
    certificacion.obra_id = this.centro_costo.id;
    this.certificaciones.push(certificacion);
  }

  guardarTodos() {
    for (let cert of this.certificaciones) {
      if (!this.itemIsValid(cert)) {
        this._notifications.error('Corrija primero los ítems con fondo rojo.');
        return;
      }
    }
    if ( !this.isAllValid()) {
      this._notifications.error('Hay más de un ítem con el mismo periodo seleccionado.');
      return;
    }
    this.isDisabled = true;
    for (let cert of this.certificaciones) {
      if (cert.pk) {
        this.registro_service.update_certificacion_proyeccion(cert).subscribe(certificacion => {
        }, error => this.handleError(error));
      } else {
        this.registro_service.create_certificacion_proyeccion(cert).subscribe(certificacion => {
        }, error => this.handleError(error));
      }
    }
    setTimeout(() => {
      this.isDisabled = false;
      this._notifications.success('Se guardó correctamente la proyección.');
    }, 1000);
  }

  eliminarCertificacion(obj: ICertificacion) {
    const dialogRef = this.modal.confirm()
    .showClose(true)
    .title('Confirmación de eliminación')
    .message(
      '¿Está seguro que desea <b>eliminar</b> este ítem de la proyección ' +
      'de certificación del sistema?<br><b>Esta acción no puede deshacerse.</b>')
    .cancelBtn('Cancelar')
    .okBtn('Eliminar')
    .open();
    dialogRef.then(
      dialog => {
        dialog.result.then(
          result => {
            this.registro_service.delete_certificacion_proyeccion(obj).subscribe(
              r => {
                this.refresh();
                this._notifications.success('Ítem eliminado correctamente.');
              },
              error => this.handleError(error));
          },
          () => {}
        );
      },
    );
  }

  _tonum(val): number {
    if (typeof val === 'number') {
      return val;
    }
    const newVal = parseFloat(val);
    if (!isNaN(newVal)) {
      return newVal;
    }
    return 0;
  }

  handleError(error: any) {
    this._notifications.error(error.statusText || 'Un error ha ocurrido. Por favor, intente nuevamente.');
  }
}
