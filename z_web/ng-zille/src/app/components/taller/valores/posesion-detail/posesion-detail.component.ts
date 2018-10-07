import { IPosesionValores } from './../../../../models/Interfaces';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TallerService } from '../../../../services/taller.service';
import { ModalService } from '../../../../services/core/modal.service';

@Component({
  selector: 'app-posesion-detail',
  templateUrl: './posesion-detail.component.html'
})
export class PosesionDetailComponent implements OnInit {


  item: IPosesionValores;
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
        '¿Desea guardar los valores de posesion?',
        'Guardado',
      () => this.guardarValor()
    ).open();
  }

  guardarValor() {
    this.tallerServ.put_posesion_valor(this.item).subscribe(
      item => this.item = item,
      err => {
        console.log(err);
        this.reset();
      }
    );
    this.to_edit(false);
  }

  reset() {
    this.tallerServ.get_posesion_valor(this.item).subscribe(
      item => this.item = item
    );
    this.to_edit(false);
  }
}
