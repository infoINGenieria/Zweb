import { ModalService } from './../../../../services/core/modal.service';
import { TallerService } from './../../../../services/taller.service';
import { ActivatedRoute } from '@angular/router';
import { IEquipoAlquiladoValores } from './../../../../models/Interfaces';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-alquilados-detail',
  templateUrl: './alquilados-detail.component.html'
})
export class AlquiladosDetailComponent implements OnInit {

  item: IEquipoAlquiladoValores;
  editing = false;

  alquiler: number;
  comentarios: string;

  constructor(
    private route: ActivatedRoute,
    public tallerServ: TallerService,
    public modal: ModalService
  ) { }

  ngOnInit() {
    this.route.params.subscribe(
      param => {
        this.item = this.tallerServ.tempStorage;
        this.alquiler = this.item.alquiler;
        this.comentarios = this.item.comentarios;
      }
    );
  }

  to_edit(val = true) {
    this.editing = val;
  }

  guardarValorModal() {
    this.modal.setUp(
        '¿Desea guardar el valor de alquiler?',
        'Guardado',
      () => this.guardarValor()
    ).open();
  }

  guardarValor() {
    this.item.alquiler = this.alquiler;
    this.item.comentarios = this.comentarios;
    this.tallerServ.put_alquilados_valor(this.item).subscribe(
      item => this.item = item,
      err => {
        console.log(err);
        this.reset();
      }
    );
    this.to_edit(false);
  }

  reset() {
    this.tallerServ.get_alquilados_valor(this.item).subscribe(
      item => {
        this.item = item;
        this.alquiler = this.item.alquiler;
        this.comentarios = this.item.comentarios;
      }
    );
    this.to_edit(false);
  }
}
