import { RouterModule, Routes } from '@angular/router';
import { AppComponent } from './app.component';

import { IndexComponent } from './components/index/index.component';
import { PresupuestoComponent } from './components/presupuesto/presupuesto.component';
import { PresupuestosComponent } from './components/presupuestos/presupuestos.component';
import { TableroControlOsComponent } from './components/tablero-control-os/tablero-control-os.component';
import { ProyeccionesComponent } from './components/proyecciones/proyecciones.component';
import { CertificacionesComponent } from './components/proyecciones/certificaciones.component';
import {
    CertificacionRealComponent, CertificacionesRealComponent,
  } from './components/certificaciones';

const APP_ROUTES: Routes = [
  { path: '', component: IndexComponent },
  { path: 'presupuestos', component: PresupuestosComponent },
  { path: 'presupuestos/nuevo', component: PresupuestoComponent },
  { path: 'presupuestos/:pk/v/:version', component: PresupuestoComponent },
  { path: 'proyecciones', component: ProyeccionesComponent },
  { path: 'proyecciones/:obra_id/certificaciones', component: CertificacionesComponent },
  { path: 'certificaciones', component: CertificacionesRealComponent },
  { path: 'certificaciones/nuevo', component: CertificacionRealComponent },
  { path: 'certificaciones/:pk', component: CertificacionRealComponent },

  { path: 'tablero-control/os', component: TableroControlOsComponent },

  { path: '**', pathMatch: 'full', redirectTo: '' }
];

export const APP_ROUTING = RouterModule.forRoot(APP_ROUTES);
