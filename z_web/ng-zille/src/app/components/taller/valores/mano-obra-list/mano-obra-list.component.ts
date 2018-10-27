import { Observable } from 'rxjs/Rx';
import { NgForm } from '@angular/forms';
import { Page } from './../../../../models/Page';
import { IPeriodo, IManoObraValores } from './../../../../models/Interfaces';
import { Component, OnInit, OnDestroy, AfterViewInit } from '@angular/core';
import { TallerService } from '../../../../services/taller.service';
import { CoreService } from '../../../../services/core/core.service';
import { Router, Event, NavigationEnd } from '@angular/router';
import { fadeInAnimation } from '../../../../_animations';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-mano-obra-list',
  templateUrl: './mano-obra-list.component.html',
  styles: [
    `:host {
      padding: 10px;
    }`
  ],
  animations: [fadeInAnimation]
})
export class ManoObraListComponent implements OnInit, OnDestroy {

  periodos: Array<IPeriodo> = [];
  valido_desde: IPeriodo;
  valores: Array<IManoObraValores> = [];
  selectedItem: IManoObraValores;
  page = new Page();
  loaded = false;

  f_valido_desde: string;

  refreshObserver: Subscription;

  constructor(
    public tallerServ: TallerService,
    public coreServ: CoreService,
    public router: Router
  ) { }

  ngOnInit() {
    this.refresh();
    this.coreServ.get_periodos_list().subscribe(
      periodos => this.periodos = periodos
    );

    this.refreshObserver = this.tallerServ.refreshListObservable.subscribe(foo => this.refresh());
  }

  ngOnDestroy() {
    this.refreshObserver.unsubscribe();
  }


  refresh(newPage?) {
    if (newPage) {
      this.page.pageNumber = newPage;
    }
    this.loaded = false;
    this.tallerServ.get_mano_obra_valores(
      this.page.pageNumber,
      this.f_valido_desde
    ).subscribe(
      valores => {
        this.valores = valores['results'] as Array<IManoObraValores>;
        this.page.pageNumber = this.page.pageNumber;
        this.page.totalElements = Number(valores['count']);
        this.page.totalPages = Math.ceil(this.page.totalElements / this.page.size) || 0;
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

  selectItem(item) {
    this.selectedItem = item;
    this.tallerServ.tempStorage = this.selectedItem;
    this.router.navigate(['/taller/valores', {
      outlets: {'details': ['mano_obra', this.selectedItem.pk]}
    }]);
  }

  newOne() {
    this.selectedItem = null;
    this.router.navigate(['/taller/valores', {
      outlets: {
        'details': null,
        'tabs': 'mano_obra_new'
      }
    }]);
  }
}
