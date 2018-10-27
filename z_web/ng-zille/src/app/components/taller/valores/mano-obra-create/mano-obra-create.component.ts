import { CoreService } from './../../../../services/core/core.service';
import { IPeriodo, IManoObraValores } from './../../../../models/Interfaces';
import { NotificationService } from './../../../../services/core/notifications.service';
import { ModalService } from './../../../../services/core/modal.service';
import { TallerService } from './../../../../services/taller.service';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-mano-obra-create',
  templateUrl: './mano-obra-create.component.html',
  styles: []
})
export class ManoObraCreateComponent implements OnInit {

  periodos: IPeriodo[] = [];

  item: IManoObraValores;

  constructor(
    public coreServ: CoreService,
    public tallerServ: TallerService,
    public modal: ModalService,
    private notification: NotificationService,
    private router: Router
  ) {
    this.item = new Object() as IManoObraValores;
    this.item.taller = 0;
    this.item.plataforma_combustible = 0;
    this.item.carretones = 0;
   }

  ngOnInit() {
    this.coreServ.get_periodos_list().subscribe(
      p => this.periodos = p
    );
  }

  guardarValorModal() {
    this.modal.setUp(
        '¿Desea guardar los valores de mano de obra?',
        'Guardado',
      () => this.guardarValor()
    ).open();
  }

  guardarValor() {
    this.tallerServ.post_mano_obra_valor(this.item).subscribe(
      item => {
        this.item = item;
        this.notification.success('Valor de mano de obra creado');
        this.router.navigate(['/taller/valores', {
          outlets: {
            'tabs': ['mano_obra'],
            'details': []
          }
        }]
        );
      },
      err => {
        console.log(err);
        this.notification.error('Ocurrió un error al guardar. Intente nuevamente.')
      }
    );
  }
}
