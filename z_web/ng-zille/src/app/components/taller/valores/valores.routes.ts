import { ManoObraListComponent } from './mano-obra-list/mano-obra-list.component';
import { TrenRodajeListComponent } from './tren-rodaje-list/tren-rodaje-list.component';
import { LubricantesListComponent } from './lubricantes-list/lubricantes-list.component';
import { Routes } from '@angular/router';
import { PosesionListComponent } from './posesion-list/posesion-list.component';
import { ReparacionesListComponent } from './reparaciones-list/reparaciones-list.component';


export const VALORES_ROUTES: Routes = [
    { path: '', redirectTo: '', pathMatch: 'full' },
    { path: 'lubricantes', component: LubricantesListComponent, outlet: 'tabs' },
    { path: 'tren_rodaje', component: TrenRodajeListComponent, outlet: 'tabs' },
    { path: 'posesion', component: PosesionListComponent, outlet: 'tabs' },
    { path: 'reparacion', component: ReparacionesListComponent, outlet: 'tabs' },
    { path: 'mano_obra', component: ManoObraListComponent, outlet: 'tabs' },
    { path: '**', pathMatch: 'full', redirectTo: '' }
  ];
