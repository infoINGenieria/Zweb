import { ModalService } from './../../../../services/core/modal.service';
import { TallerService } from './../../../../services/taller.service';
import { ActivatedRoute } from '@angular/router';
import { ITrenRodajeValores } from './../../../../models/Interfaces';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-tren-rodaje-detail',
  templateUrl: './tren-rodaje-detail.component.html'
})
export class TrenRodajeDetailComponent implements OnInit {

  item: ITrenRodajeValores;
  editing = false;

  constructor(
    private route: ActivatedRoute,
    public tallerServ: TallerService,
    public modal: ModalService
  ) { }

  ngOnInit() {
    this.route.params.subscribe(
      param => {
        this.item = this.tallerServ.tempStorage;
      }
    );
  }

  to_edit(val = true) {
    this.editing = val;
  }

  guardarValorModal() {
    this.modal.setUp(
        '¿Desea guardar los valores de tren de rodaje?',
        'Guardado',
      () => this.guardarValor()
    ).open();
  }

  guardarValor() {
    this.tallerServ.put_tren_rodaje_valor(this.item).subscribe(
      item => this.item = item,
      err => {
        console.log(err);
        this.reset();
      }
    );
    this.to_edit(false);
  }

  reset() {
    this.tallerServ.get_tren_rodaje_valor(this.item).subscribe(
      item => this.item = item
    );
    this.to_edit(false);
  }
}
