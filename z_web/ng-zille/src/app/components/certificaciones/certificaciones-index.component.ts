import { fadeInAnimation } from './../../_animations/fade-in.animation';
import { Component } from '@angular/core';

@Component({
  selector: 'app-certificaciones-index',
  template: `
    <h1><a class="btn btn-default" [routerLink]="['']"><i class="fa fa-chevron-left"></i> </a>
      Certificaciones</h1>
    <div class="row zille-tools">
      <div class="col-lg-6 col-md-9" [@fadeInAnimation]>
        <a class="btn btn-primary btn-lg btn-block" [routerLink]="['/certificaciones', 'real']">
            <div class="col-xs-2">
                <i class="fa fa-handshake-o"></i>
            </div>
            <div class="col-xs-10 text-left">
                <h4><strong>Certificaciones</strong></h4>
                <h5>Reales</h5>
            </div>
        </a>
      </div>
      <div class="col-lg-6 col-md-9" [@fadeInAnimation]>
        <a class="btn btn-info btn-lg btn-block" [routerLink]="['/certificaciones', 'proyeccion']">
          <div class="col-xs-2">
              <i class="fa fa-certificate"></i>
          </div>
          <div class="col-xs-10 text-left">
              <h4><strong>Proyección de Certificaciones</strong></h4>
              <h5>Esperadas</h5>
          </div>
        </a>
      </div>
    </div>
  `,
  animations: [fadeInAnimation],
})
export class CertificacionesIndexComponent {
  constructor() { }
}
