import { IReparacionesValores } from './../../../../models/Interfaces';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TallerService } from '../../../../services/taller.service';
import { ModalService } from '../../../../services/core/modal.service';

@Component({
  selector: 'app-reparaciones-detail',
  templateUrl: './reparaciones-detail.component.html'
})
export class ReparacionesDetailComponent implements OnInit {


  item: IReparacionesValores;
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

}
