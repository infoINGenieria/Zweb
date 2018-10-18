import { PaginationComponent } from './components/shared/page.component';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule, LOCALE_ID } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NvD3Module } from 'ng2-nvd3';
import { Ng2StickyModule } from 'ng2-sticky';

import { NgxSmartModalModule } from 'ngx-smart-modal';
// import { CurrencyMaskModule } from 'ng2-currency-mask';
import { ToastaModule } from 'ngx-toasta';
// import { MyDatePickerModule } from 'mydatepicker';
import { DpDatePickerModule } from 'ng2-date-picker';
import { APP_ROUTING } from './app.routes';

// Services
import { BaseApiService } from './services/base-api/base-api.service';
import { CoreService } from './services/core/core.service';
import { TableroService } from './services/tablero.service';
import { RegistroService } from './services/registro/registro.service';
import { NotificationService } from './services/core/notifications.service';
import { PresupuestosService } from './services/presupuestos/presupuestos.service';
import { AvanceObraService } from './services/avanceobra.service';
import { ProyeccionesService} from './services/proyecciones.service';
import { TallerService } from './services/taller.service';

// Own
import { AppComponent } from './app.component';
import { PresupuestoComponent } from './components/presupuesto/presupuesto.component';
import { PresupuestosComponent } from './components/presupuestos/presupuestos.component';
import { AvanceObraComponent } from './components/proyecciones/avance-obra.component';
import {
  CertificacionesRealComponent, CertificacionRealComponent,
} from './components/certificaciones';
import { IndexComponent } from './components/index/index.component';
import { TableroControlOsComponent } from './components/tablero-control-os/tablero-control-os.component';
import { ProyeccionesComponent } from './components/proyecciones/proyecciones.component';
import { CertificacionesComponent } from './components/proyecciones/certificaciones.component';
import { CostoComponent } from './components/proyecciones/costo.component';

// d3 and nvd3 should be included somewhere
import 'd3';
import 'nvd3';
import 'save-svg-as-png';

// pipe
import { MonedaPipe } from './pipes/moneda.pipe';
import { PorcientoPipe } from './pipes/porciento.pipe';

// directives
import { MyCurrencyFormatterDirective } from './directives/currency-formatter.directive';
import { StickyBelowViewDirective } from './directives/sticky-below-view.directive';

import { registerLocaleData } from '@angular/common';
import localeEs from '@angular/common/locales/es';
import { TallerComponent } from './components/taller/taller.component';
import { ParametrosGralComponent } from './components/taller/parametros-gral/parametros-gral.component';
import { EquiposComponent } from './components/taller/equipos/equipos.component';
import { EquipoDetailComponent } from './components/taller/equipos/equipo-detail.component';
import { ParametrosGralPageComponent } from './components/taller/parametros-gral/parametros-gral-page.component';
import { AsistenciasComponent } from './components/taller/asistencia/asistencias.component';
import { AsistenciaFormComponent } from './components/taller/asistencia/asistencia-form.component';
import { AsistenciaByEquipoComponent } from './components/taller/reports/asistencia-by-equipo.component';
import { TableroTallerComponent } from './components/taller/tablero/tablero-taller.component';
import { ValoresListComponent } from './components/taller/valores/valores-list.component';
import { LubricantesListComponent } from './components/taller/valores/lubricantes-list/lubricantes-list.component';
import { ModalComponent } from './components/shared/modal/modal.component';
import { ModalService } from './services/core/modal.service';
import { LubricantesDetailComponent } from './components/taller/valores/lubricantes-detail/lubricantes-detail.component';
import { TrenRodajeListComponent } from './components/taller/valores/tren-rodaje-list/tren-rodaje-list.component';
import { TrenRodajeDetailComponent } from './components/taller/valores/tren-rodaje-detail/tren-rodaje-detail.component';
import { PosesionDetailComponent } from './components/taller/valores/posesion-detail/posesion-detail.component';
import { PosesionListComponent } from './components/taller/valores/posesion-list/posesion-list.component';
import { ReparacionesListComponent } from './components/taller/valores/reparaciones-list/reparaciones-list.component';
import { ReparacionesDetailComponent } from './components/taller/valores/reparaciones-detail/reparaciones-detail.component';
import { ManoObraDetailComponent } from './components/taller/valores/mano-obra-detail/mano-obra-detail.component';
import { ManoObraListComponent } from './components/taller/valores/mano-obra-list/mano-obra-list.component';
import { AlquiladosListComponent } from './components/taller/valores/alquilados-list/alquilados-list.component';
import { AlquiladosDetailComponent } from './components/taller/valores/alquilados-detail/alquilados-detail.component';
import { MarkupDetailComponent } from './components/taller/valores/markup-detail/markup-detail.component';
import { MarkupListComponent } from './components/taller/valores/markup-list/markup-list.component';

registerLocaleData(localeEs, 'es-AR');

@NgModule({
  declarations: [
    AppComponent,
    PresupuestosComponent,
    PresupuestoComponent,
    IndexComponent,
    CertificacionesRealComponent,
    CertificacionRealComponent,
    TableroControlOsComponent,
    ProyeccionesComponent,
    CertificacionesComponent,
    MonedaPipe,
    MyCurrencyFormatterDirective,
    StickyBelowViewDirective,
    PorcientoPipe,
    AvanceObraComponent,
    CostoComponent,
    TallerComponent,
    ParametrosGralComponent,
    EquiposComponent,
    EquipoDetailComponent,
    PaginationComponent,
    ParametrosGralPageComponent,
    AsistenciasComponent,
    AsistenciaFormComponent,
    AsistenciaByEquipoComponent,
    TableroTallerComponent,
    ValoresListComponent,
    LubricantesListComponent,
    ModalComponent,
    LubricantesDetailComponent,
    TrenRodajeListComponent,
    TrenRodajeDetailComponent,
    PosesionDetailComponent,
    PosesionListComponent,
    ReparacionesListComponent,
    ReparacionesDetailComponent,
    ManoObraDetailComponent,
    ManoObraListComponent,
    StickyBelowViewDirective,
    AlquiladosListComponent,
    AlquiladosDetailComponent,
    MarkupDetailComponent,
    MarkupListComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule,
    ToastaModule.forRoot(),
    NgxSmartModalModule.forRoot(),
    DpDatePickerModule,
    APP_ROUTING,
    BrowserAnimationsModule,
    NvD3Module,
    Ng2StickyModule
    // CurrencyMaskModule
  ],
  providers: [
    {provide: LOCALE_ID, useValue: 'es-AR'},
    BaseApiService,
    PresupuestosService,
    CoreService,
    NotificationService,
    RegistroService,
    TableroService,
    AvanceObraService,
    ProyeccionesService,
    TallerService,
    ModalService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
