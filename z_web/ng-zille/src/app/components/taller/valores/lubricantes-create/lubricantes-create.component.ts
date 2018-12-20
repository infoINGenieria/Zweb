import { Component, OnInit } from '@angular/core';
import { Periodo } from './../../../../models/Periodo';
import { CoreService } from './../../../../services/core/core.service';
import { Router } from '@angular/router';
import { TallerService } from './../../../../services/taller.service';
import { ModalService } from './../../../../services/core/modal.service';
import { NotificationService } from './../../../../services/core/notifications.service';
import { ILubricanteItem } from './../../../../models/Interfaces';

import * as moment from 'moment';

// clase para enviar los nuevos valores
class NewValueLubricante {
  item_id: number;
  valor: number;
  nuevo_valor: number;

  constructor(item_id: number, valor = 0) {
    this.item_id = item_id;
    this.valor = valor;
    this.nuevo_valor = valor;
  }
}

@Component({
  selector: 'app-lubricantes-create',
  templateUrl: './lubricantes-create.component.html',
  styles: []
})
export class LubricantesCreateComponent implements OnInit {

  sel_periodo: Periodo;
  current_periodo_id: number;
  periodos: Periodo[] = [];

  itemes: ILubricanteItem[] = [];
  valores: NewValueLubricante[] = [];

  nuevos_valores: NewValueLubricante[] = [];

  is_loading = true;

  constructor(public coreServ: CoreService,
    public router: Router,
    public tallerServ: TallerService,
    public modal: ModalService,
    public notificationServ: NotificationService) { }


    /*

    Ajustar envio de valores y lo que genero en este comenponente

    */
    ngOnInit() {
      this.coreServ.get_periodos_list().subscribe(
        periodo => this.periodos = periodo as Periodo[]
      );

      this.tallerServ.get_last_values_from_items_lubricantes().subscribe(
        valores => {
          this.current_periodo_id = valores['periodo_id'];
          this.valores = valores['valores'] as NewValueLubricante[];
          this.tallerServ.get_items_lubricantes().subscribe(
            param => {
              this.itemes = param['results'] as Array<ILubricanteItem>;
              this.itemes.forEach(value => {
                this.nuevos_valores.push(new NewValueLubricante(value.pk, this.currentValor(value)));
              });
              this.is_loading = false;
            }
          );
        }
      );
    }

    get get_periodos_disponibles(): Periodo[] {
      try {
        const currentPeriodo = this.periodos.find(a => a.pk === this.current_periodo_id) as Periodo;
        const limit = moment(currentPeriodo.fecha_inicio, 'DD/MM/YYYY');
        return this.periodos.filter(a => limit.isBefore(moment(a.fecha_inicio, 'DD/MM/YYYY')));
      } catch (ex) {
        return [];
      }
    }

    currentValor(item: ILubricanteItem): number {
      try {
        return this.valores.find(a => a.item_id === item.pk).valor;
      } catch(ex) {
        return 0;
      }
    }

    get_descripcion(item_pk: number) {
      return this.itemes.find(a => a.pk === item_pk).descripcion;
    }

    diffStr(item: NewValueLubricante): string {
      const _diff = ((item.nuevo_valor / item.valor) - 1) * 100;
      if (isNaN(_diff) || item.valor === 0) { return '-'; }
      if (_diff > 0) {
        return `+${_diff.toFixed(2)} %`;
      } else {
        return `${_diff.toFixed(2)} %`;
      }
    }

    crearNuevosValoresModal() {
      this.modal.setUp(
        '¿Continuar?',
        'Crear nuevos valores de lubricantes y f. hidráulicos',
      () => this.crearNuevosValores()
    ).open();
    }


    crearNuevosValores() {

      this.tallerServ.create_new_values_lubricantes(this.sel_periodo, this.nuevos_valores).subscribe(
        data => {
          if (data.status === 'ok') {
            this.notificationServ.success('Exito: ' + data.message);
            this.router.navigate(['/taller/valores', {
              outlets: {
                'details': null,
                'tabs': 'lubricantes'
              }
            }]);
          } else {
            this.notificationServ.error('Error: ' + data.message);
          }
        },
        err => {
          console.error(err);
          this.notificationServ.error('Error en la comunicación. Intento nuevamente');
        }
      );
    }

}
