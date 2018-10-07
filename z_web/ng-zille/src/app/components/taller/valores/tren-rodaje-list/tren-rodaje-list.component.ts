import { NgForm } from '@angular/forms';
import { Router } from '@angular/router';
import { CoreService } from './../../../../services/core/core.service';
import { TallerService } from './../../../../services/taller.service';
import { Page } from './../../../../models/Page';
import { IPeriodo, ITrenRodajeValores } from './../../../../models/Interfaces';
import { fadeInAnimation } from './../../../../_animations/fade-in.animation';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-tren-rodaje-list',
  templateUrl: './tren-rodaje-list.component.html',
  styleUrls: ['./tren-rodaje-list.component.css'],
  animations: [fadeInAnimation]
})
export class TrenRodajeListComponent implements OnInit {

  periodos: Array<IPeriodo> = [];
  valido_desde: IPeriodo;
  valores: Array<ITrenRodajeValores> = [];
  selectedItem: ITrenRodajeValores;
  page = new Page();
  loaded = false;

  f_valido_desde: string;
  f_equipo: string;
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
  }

  refresh(newPage?) {
    if (newPage) {
      this.page.pageNumber = newPage;
    }
    this.loaded = false;
    this.tallerServ.get_tren_rodaje_valores(
      this.page.pageNumber,
      this.f_valido_desde,
      this.f_equipo
    ).subscribe(
      valores => {
        this.valores = valores['results'] as Array<ITrenRodajeValores>;
        this.page.pageNumber = this.page.pageNumber;
        this.page.totalElements = Number(valores['count']);
        this.page.totalPages = Math.ceil(this.page.totalElements / this.page.size) || 0;
        this.loaded = true;
      }
    );
  }

  filterList(form: NgForm) {
    this.page.pageNumber = 1;
    const { valido_desde, equipo } = form.value;

    this.f_valido_desde = valido_desde;
    this.f_equipo = equipo;
    this.loaded = false;
    this.refresh();
  }

  cleanFilter(form: NgForm) {
    form.reset();
    this.page.pageNumber = 1;
    this.f_valido_desde = '';
    this.f_equipo = '';
    this.refresh();
  }

  selectItem(item) {
    this.selectedItem = item;
    this.tallerServ.tempStorage = this.selectedItem;
    this.router.navigate(['/taller/valores', {
      outlets: {'details': ['tren_rodaje', this.selectedItem.pk]}
    }]);
  }
}
