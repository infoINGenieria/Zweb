import { CoreService } from '../../../services/core/core.service';
import { IPeriodo } from '../../../models/Interfaces';
import { NgForm } from '@angular/forms';
import { PaginationComponent } from '../../shared/page.component';
import { Page } from '../../../models/Page';
import { Modal } from 'ngx-modialog/plugins/bootstrap/src/ngx-modialog-bootstrap.ng-flat';
import { NotificationService } from '../../../services/core/notifications.service';
import { IParametrosGenerales } from '../../../models/Interfaces';
import { fadeInAnimation } from '../../../_animations/fade-in.animation';
import { TallerService } from '../../../services/taller.service';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-parametros-gral',
  templateUrl: './parametros-gral.component.html',
  styleUrls: ['./parametros-gral.component.css'],
  animations: [fadeInAnimation]
})
export class ParametrosGralComponent extends PaginationComponent implements OnInit {

  parametros_generales: Array<IParametrosGenerales> = [];
  periodos: IPeriodo[] = [];

  loaded = false;

  // filter
  f_valido_desde = '';

  constructor(
    private tallerServ: TallerService,
    private coreServ: CoreService,
    private notify_service: NotificationService,
    private modal: Modal
  ) {
    super();
  }

  ngOnInit() {
    this.coreServ.get_periodos_list().subscribe(p => {
      this.periodos = p as IPeriodo[];
    });

    this.refresh();
  }

  refresh() {
    this.loaded = false;
    this.tallerServ.get_parametros_generales_list(
      this.page.pageNumber,
      this.f_valido_desde
    ).subscribe(
      parametros => {
        this.parametros_generales = parametros['results'] as Array<IParametrosGenerales>;
        this.page.pageNumber = this.page.pageNumber;
        this.page.size = this.parametros_generales.length;
        this.page.totalElements = Number.parseInt(parametros.count);
        this.page.totalPages = parseInt(
          Number(this.page.totalElements / this.parametros_generales.length + 0.5).toFixed(0), 0);
        this.loaded = true;
      }
    );
  }

  filterList(form: NgForm) {
    this.page.pageNumber = 1;
    const { valido_desde } = form.value;

    this.f_valido_desde = valido_desde;
    this.loaded = false;
    this.refresh();
  }

  cleanFilter(form: NgForm) {
    form.reset();
    this.page.pageNumber = 1;
    this.f_valido_desde = '';
    this.refresh();
  }


  onBtNext() {
    this.page.pageNumber += 1;
    if (this.page.pageNumber > this.page.totalPages) {
      this.page.pageNumber = this.page.totalPages;
    } else {
      this.refresh();
    }
  }

  onBtPrevious() {
    this.page.pageNumber -= 1;
    if (this.page.pageNumber < 1) {
      this.page.pageNumber = 1;
    } else {
      this.refresh();
    }
  }

  get canPrevious() {
    return this.page.pageNumber > 1;
  }

  get canNext() {
    return this.page.pageNumber < this.page.totalPages;
  }

  handleError(error: any) {
    this.notify_service.error(error._body || error);
  }
}
