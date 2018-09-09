import { AsistenciaByEquipoComponent } from './components/taller/reports/asistencia-by-equipo.component';
import { AsistenciaFormComponent } from './components/taller/asistencia/asistencia-form.component';
import { ParametrosGralPageComponent } from './components/taller/parametros-gral/parametros-gral-page.component';
import { EquipoDetailComponent } from './components/taller/equipos/equipo-detail.component';
import { EquiposComponent } from './components/taller/equipos/equipos.component';
import { ParametrosGralComponent } from './components/taller/parametros-gral/parametros-gral.component';
import { TallerComponent } from './components/taller/taller.component';
import { RouterModule, Routes } from '@angular/router';
import { AppComponent } from './app.component';

import { IndexComponent } from './components/index/index.component';
import { PresupuestoComponent } from './components/presupuesto/presupuesto.component';
import { PresupuestosComponent } from './components/presupuestos/presupuestos.component';
import { TableroControlOsComponent } from './components/tablero-control-os/tablero-control-os.component';
import { ProyeccionesComponent } from './components/proyecciones/proyecciones.component';
import { CertificacionesComponent } from './components/proyecciones/certificaciones.component';
import { CostoComponent } from './components/proyecciones/costo.component';
import { AvanceObraComponent } from './components/proyecciones/avance-obra.component';
import {
    CertificacionRealComponent, CertificacionesRealComponent,
  } from './components/certificaciones';
import { AsistenciasComponent } from './components/taller/asistencia/asistencias.component';

const APP_ROUTES: Routes = [
  { path: '', component: IndexComponent },
  { path: 'presupuestos', component: PresupuestosComponent },
  { path: 'presupuestos/nuevo', component: PresupuestoComponent },
  { path: 'presupuestos/:pk/v/:version', component: PresupuestoComponent },
  { path: 'proyecciones', component: ProyeccionesComponent },
  { path: 'proyecciones/:obra_id/certificaciones', component: CertificacionesComponent },
  { path: 'proyecciones/:obra_id/certificaciones/:rev', component: CertificacionesComponent },
  { path: 'proyecciones/:obra_id/avances-obra', component: AvanceObraComponent },
  { path: 'proyecciones/:obra_id/avances-obra/:rev', component: AvanceObraComponent },
  { path: 'proyecciones/:obra_id/costo', component: CostoComponent },
  { path: 'proyecciones/:obra_id/costo/:rev', component: CostoComponent },
  { path: 'certificaciones', component: CertificacionesRealComponent },
  { path: 'certificaciones/nuevo', component: CertificacionRealComponent },
  { path: 'certificaciones/:pk', component: CertificacionRealComponent },

  { path: 'tablero-control/os', component: TableroControlOsComponent },

  { path: 'taller', component: TallerComponent },
  { path: 'taller/equipos', component: EquiposComponent },
  { path: 'taller/equipos/:pk', component: EquipoDetailComponent },
  { path: 'taller/parametros/general', component: ParametrosGralComponent },
  { path: 'taller/parametros/general/:pk', component: ParametrosGralPageComponent },
  { path: 'taller/asistencia', component: AsistenciasComponent },
  { path: 'taller/asistencia/:pk/:clone', component: AsistenciaFormComponent },
  { path: 'taller/asistencia/:pk', component: AsistenciaFormComponent },
  { path: 'taller/reportes/asistencia', component: AsistenciaByEquipoComponent },

  { path: '**', pathMatch: 'full', redirectTo: '' }
];

export const APP_ROUTING = RouterModule.forRoot(APP_ROUTES);
