import { IManoObraValores } from './../../../../models/Interfaces';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TallerService } from '../../../../services/taller.service';
import { ModalService } from '../../../../services/core/modal.service';

@Component({
  selector: 'app-mano-obra-detail',
  templateUrl: './mano-obra-detail.component.html',
})
export class ManoObraDetailComponent implements OnInit {

  item: IManoObraValores;
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
        '¿Desea guardar los valores de mano de obra?',
        'Guardado',
      () => this.guardarValor()
    ).open();
  }

  guardarValor() {
    this.tallerServ.put_mano_obra_valor(this.item).subscribe(
      item => this.item = item,
      err => {
        console.log(err);
        this.reset();
      }
    );
    this.to_edit(false);
  }

  reset() {
    this.tallerServ.get_mano_obra_valor(this.item).subscribe(
      item => this.item = item
    );
    this.to_edit(false);
  }
}
