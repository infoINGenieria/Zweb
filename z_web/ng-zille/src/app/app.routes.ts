import { IndexComponent } from './components/index/index.component';
import { TipoItemPresupuestoComponent } from './components/tipo-item-presupuesto/tipo-item-presupuesto.component';
import { PresupuestoComponent } from './components/presupuesto/presupuesto.component';
import { PresupuestosComponent } from './components/presupuestos/presupuestos.component';
import { AppComponent } from './app.component';
import { RouterModule, Routes } from '@angular/router';

import {
  CertificacionesProyeccionComponent, CertificacionesIndexComponent,
  CertificacionRealComponent, CertificacionesRealComponent,
  CertificacionProyeccionComponent
} from './components/certificaciones';

const APP_ROUTES: Routes = [
  { path: '', component: IndexComponent },
  { path: 'tipo-items', component: TipoItemPresupuestoComponent },
  { path: 'presupuestos', component: PresupuestosComponent },
  { path: 'presupuestos/nuevo', component: PresupuestoComponent },
  { path: 'presupuestos/:pk/v/:version', component: PresupuestoComponent },
  { path: 'certificaciones/index', component: CertificacionesIndexComponent },
  { path: 'certificaciones/real', component: CertificacionesRealComponent },
  { path: 'certificaciones/real/nuevo', component: CertificacionRealComponent },
  { path: 'certificaciones/real/:pk', component: CertificacionRealComponent },
  { path: 'certificaciones/proyeccion', component: CertificacionesProyeccionComponent },
  { path: 'certificaciones/proyeccion/nuevo', component: CertificacionProyeccionComponent },
  { path: 'certificaciones/proyeccion/:pk', component: CertificacionProyeccionComponent },

  { path: '**', pathMatch: 'full', redirectTo: '' }
];

export const APP_ROUTING = RouterModule.forRoot(APP_ROUTES);
