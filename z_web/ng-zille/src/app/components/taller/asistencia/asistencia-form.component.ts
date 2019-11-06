import { ICentroCostoByDeposito } from './../../../models/Interfaces';
import { ModalService } from './../../../services/core/modal.service';
import { ActivatedRoute, Router } from '@angular/router';
import { NotificationService } from '../../../services/core/notifications.service';
import { TallerService } from '../../../services/taller.service';
import { IDatePickerConfig, ECalendarValue } from 'ng2-date-picker';
import { fadeInAnimation } from '../../../_animations/fade-in.animation';
import { Component, OnInit, NgZone } from '@angular/core';
import { IAsistencia, IEquipo, IRegistroAsistencia, ICentroCosto } from '../../../models/Interfaces';
import { CoreService } from '../../../services/core/core.service';
import { RegistroAsistencia } from '../../../models/RegistroAsistencia';

import * as moment from 'moment';

@Component({
  selector: 'app-asistencia-form',
  templateUrl: './asistencia-form.component.html',
  styleUrls: ['./asistencia-form.component.scss'],
  animations: [fadeInAnimation]
})
export class AsistenciaFormComponent implements OnInit {

  asistencia: IAsistencia = null;
  equipos: IEquipo[] = [];
  excluidos: IEquipo[] = [];
  centros_costos: ICentroCostoByDeposito[] = [];
  centros_costos_all: ICentroCosto[] = [];
  asistencia_pk: any;

  initialLoading = true;

  is_cloning = false;


  constructor(
    private tallerServ: TallerService,
    private coreServ: CoreService,
    private notify_service: NotificationService,
    private modal: ModalService,
    private route: ActivatedRoute,
    private router: Router,
    private ngZone: NgZone
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
            this.newAsistenciaAndfillRegistros();
            this.initialLoading = false;
          } else {
            this.refresh();
          }
        });
      },
      error => this.handleError(error)
    );

    // centros de costos
    this.coreServ.get_centro_costos_by_deposito().subscribe(
      cc => this.centros_costos = cc as ICentroCostoByDeposito[],
      error => this.handleError(error)
    );
    this.coreServ.get_centro_costos_activos_list().subscribe(
      cc => this.centros_costos_all = cc as ICentroCosto[],
      error => this.handleError(error)
    );

  }

  newAsistenciaAndfillRegistros() {
    // traer ultimo registro
    this.asistencia = new Object() as IAsistencia;
    this.asistencia.registros = new Array<IRegistroAsistencia>();
    this.asistencia.dia =  moment().format('DD/MM/YYYY');
    for (const eq of this.equipos) {
      const registro = new RegistroAsistencia();
      registro.equipo = eq;
      registro.equipo_id = eq.id;
      this.asistencia.registros.push(registro);
    }
  }

  refresh() {
    this.tallerServ.get_asistencia(this.asistencia_pk).subscribe(
      asistencia => {
        this.asistencia = asistencia;
        this.excluidos = this.equipos.filter(eq => !this.asistencia.registros.find(reg => reg.equipo_id === eq.id));
        this.initialLoading = false;
    });
  }

  set_cc_by_deposito(val, i) {
    const id = this.get_id_by_deposito(val);
    if (id) {
      this.asistencia.registros[i].centro_costo_id = id;
    }
  }

  get_id_by_deposito(deposito) {
    const item = this.get_cc_by_deposito(deposito);
    if (item) {
      return item.id;
    }
    return null;
  }

  get_deposito_by_id(id: number) {
    const item = this.centros_costos.find(a => a.id == id);
    if (item) {
      return item.deposito;
    }
    return null;
  }


  get_cc_by_deposito(deposito: string) {
    const cc_match = this.centros_costos.filter(a => a.deposito.toUpperCase().startsWith(deposito.toUpperCase()));
    if (cc_match.length === 1) {
      return cc_match[0];
    }
    return null;
  }
  /*
  cc_selected(deposito: number, indx: number) {
    const cc = this.get_cc_by_deposito(deposito);
    if (cc) {
      this.registros[indx].centro_costo_id = cc.id;
      return cc.codigo;
    }
    if (deposito) {
      this.registros[indx].centro_costo_id = null;
      return 'No encontrado';
    }
    return '';
  }
  */

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
    let valid = true;
    valid = this.asistencia.registros.filter(reg => !reg.centro_costo_id ).length === 0;
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
    console.log(this.asistencia);
    this.modal.setUp(
      `¿Desea guardar la asistencia?`,
      `Asistencia de ${this.asistencia.dia}`,
      () => this.guardar_asistencia()
    ).open();
  }

  clonar_asistencia_modal() {
    this.modal.setUp(
      `Está creando una nueva asistencia a partir de la seleccionada. ¿Desea continuar?`,
      `Asistencia de ${this.asistencia.dia}`,
      () => this.clonar_asistencia()
    ).open();
  }

  handleError(error: any) {
    this.notify_service.error(error._body || error);
  }

  incluirEquipo(equipo: IEquipo) {
    this.asistencia.registros.push(new RegistroAsistencia({
      equipo: equipo,
      equipo_id: equipo.id,
      centro_costo: null,
      centro_costo_id: null
    }));
    this.excluidos.splice(this.excluidos.indexOf(equipo), 1);
  }

  excluirEquipo(req: IRegistroAsistencia) {
    this.excluidos.unshift(req.equipo);
    this.asistencia.registros.splice(this.asistencia.registros.indexOf(req), 1);
  }

  keytab(event) {
    const element = event.srcElement.nextElementSibling; // get the sibling element
    if (element == null) { // check if its null
        return;
    } else {
        element.focus();   // focus if not null
    }
  }

}
