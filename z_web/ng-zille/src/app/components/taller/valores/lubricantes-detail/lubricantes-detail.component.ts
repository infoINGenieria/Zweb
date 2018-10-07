import { ModalService } from './../../../../services/core/modal.service';
import { ILubricantesValoresItem } from './../../../../models/Interfaces';
import { ActivatedRoute } from '@angular/router';
import { Component, OnInit } from '@angular/core';
import { ILubricantesValores } from '../../../../models/Interfaces';
import { TallerService } from '../../../../services/taller.service';

@Component({
  selector: 'app-lubricantes-detail',
  templateUrl: './lubricantes-detail.component.html',
  styleUrls: ['./lubricantes-detail.component.css']
})
export class LubricantesDetailComponent implements OnInit {

  item: ILubricantesValores;
  editing = false;

  public constructor(
    private route: ActivatedRoute,
    public tallerServ: TallerService,
    public modal: ModalService
    ) {
  }

  ngOnInit() {
    this.route.params.subscribe(
      param => {
        this.item = this.tallerServ.tempStorage;
      }
    );
  }

  trackByIndex(index: number, item: ILubricantesValoresItem) {
    return index;
  }

  to_edit(val = true) {
    this.editing = val;
  }

  get_costo_mesual_calculado(item: ILubricantesValoresItem) {
      return item.parametros.cambios_por_anio * item.parametros.volumen_por_cambio * item.valor_unitario / 12;
  }

  guardarValorModal() {
    this.modal.setUp(
        '¿Desea guardar los valores de lubricantes?',
        'Guardado',
      () => this.guardarValor()
    ).open();
  }

  guardarValor() {
    this.tallerServ.put_lubricante_valor(this.item).subscribe(
      item => this.item = item,
      err => {
        console.log(err);
        this.reset();
      }
    );
    this.to_edit(false);
  }

  reset() {
    this.tallerServ.get_lubricante_valor(this.item).subscribe(
      item => this.item = item
    );
    this.to_edit(false);
  }
}
