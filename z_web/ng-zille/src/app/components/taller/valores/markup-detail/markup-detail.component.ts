import { Component, OnInit } from '@angular/core';
import { IEquipoMarkupValores } from '../../../../models/Interfaces';
import { ActivatedRoute } from '@angular/router';
import { TallerService } from '../../../../services/taller.service';
import { ModalService } from '../../../../services/core/modal.service';

@Component({
  selector: 'app-markup-detail',
  templateUrl: './markup-detail.component.html',
  styles: []
})
export class MarkupDetailComponent implements OnInit {

  item: IEquipoMarkupValores;
  editing = false;
  markup: number;

  constructor(
    private route: ActivatedRoute,
    public tallerServ: TallerService,
    public modal: ModalService
  ) { }

  ngOnInit() {
    this.route.params.subscribe(
      param => {
        if (param) {
          this.item = this.tallerServ.tempStorage;
          this.markup = this.item ? this.item.markup : 0;

        }
      }
    );
  }

  to_edit(val = true) {
    this.editing = val;
  }

  guardarValorModal() {
    this.modal.setUp(
        '¿Desea guardar los valores de markup?',
        'Guardado',
      () => this.guardarValor()
    ).open();
  }

  guardarValor() {
    const old = this.item.markup;
    this.item.markup = this.markup;
    this.tallerServ.put_markup_valor(this.item).subscribe(
      item => {
        this.item = item;
        this.markup = this.item.markup;
      },
      err => {
        this.item.markup = old;
        console.log(err);
        this.reset();
      }
    );
    this.to_edit(false);
  }

  reset() {
    this.tallerServ.get_markup_valor(this.item).subscribe(
      item => {
        this.item = item;
        this.markup = item.markup;
      }
    );
    this.to_edit(false);
  }
}
