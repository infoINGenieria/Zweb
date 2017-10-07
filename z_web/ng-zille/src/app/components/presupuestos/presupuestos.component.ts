import { fadeInAnimation } from './../../_animations/fade-in.animation';
import { itemAnim } from './../../_animations/itemAnim';
import { slideInOutAnimation } from './../../_animations/slide-in-out.animation';
import { Component, OnInit } from '@angular/core';

import { PresupuestosService } from './../../services/presupuestos/presupuestos.service';
import { IPresupuesto } from './../../models/Interfaces';

import { trigger, style, transition, animate, group } from '@angular/animations';
@Component({
  selector: 'app-presupuestos',
  templateUrl: './presupuestos.component.html',
  styleUrls: ['./presupuestos.component.css'],
  animations: [fadeInAnimation]
})
export class PresupuestosComponent implements OnInit {

  presupuestos: IPresupuesto[] = [];
  loaded = false;
  constructor(private presupuestos_service: PresupuestosService) { }

  ngOnInit() {
    this.presupuestos_service.get_presupuestos().subscribe(presupuestos => {
      this.presupuestos = presupuestos as IPresupuesto[];
      this.loaded = true;
    });
  }

}
