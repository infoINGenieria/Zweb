import { AlquiladosDetailComponent } from './alquilados-detail/alquilados-detail.component';
import { ManoObraDetailComponent } from './mano-obra-detail/mano-obra-detail.component';
import { ReparacionesDetailComponent } from './reparaciones-detail/reparaciones-detail.component';
import { TrenRodajeDetailComponent } from './tren-rodaje-detail/tren-rodaje-detail.component';
import { LubricantesDetailComponent } from './lubricantes-detail/lubricantes-detail.component';
import { ManoObraListComponent } from './mano-obra-list/mano-obra-list.component';
import { TrenRodajeListComponent } from './tren-rodaje-list/tren-rodaje-list.component';
import { LubricantesListComponent } from './lubricantes-list/lubricantes-list.component';
import { Routes } from '@angular/router';
import { PosesionListComponent } from './posesion-list/posesion-list.component';
import { ReparacionesListComponent } from './reparaciones-list/reparaciones-list.component';
import { PosesionDetailComponent } from './posesion-detail/posesion-detail.component';
import { AlquiladosListComponent } from './alquilados-list/alquilados-list.component';
import { MarkupListComponent } from './markup-list/markup-list.component';
import { MarkupDetailComponent } from './markup-detail/markup-detail.component';


export const VALORES_ROUTES: Routes = [
    { path: '', redirectTo: '', pathMatch: 'full' },
    { path: 'lubricantes', component: LubricantesListComponent, outlet: 'tabs' },
    { path: 'lubricantes/:pk', component: LubricantesDetailComponent, outlet: 'details' },
    { path: 'tren_rodaje', component: TrenRodajeListComponent, outlet: 'tabs' },
    { path: 'tren_rodaje/:pk', component: TrenRodajeDetailComponent, outlet: 'details' },
    { path: 'posesion', component: PosesionListComponent, outlet: 'tabs' },
    { path: 'posesion/:pk', component: PosesionDetailComponent, outlet: 'details' },
    { path: 'reparaciones', component: ReparacionesListComponent, outlet: 'tabs' },
    { path: 'reparaciones/:pk', component: ReparacionesDetailComponent, outlet: 'details' },
    { path: 'mano_obra', component: ManoObraListComponent, outlet: 'tabs' },
    { path: 'mano_obra/:pk', component: ManoObraDetailComponent, outlet: 'details' },
    { path: 'alquilados', component: AlquiladosListComponent, outlet: 'tabs' },
    { path: 'alquilados/:pk', component: AlquiladosDetailComponent, outlet: 'details' },
    { path: 'markup', component: MarkupListComponent, outlet: 'tabs' },
    { path: 'markup/:pk', component: MarkupDetailComponent, outlet: 'details' },
    { path: '**', pathMatch: 'full', redirectTo: '' }
  ];
