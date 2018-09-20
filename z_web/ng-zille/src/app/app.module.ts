import { PaginationComponent } from './components/shared/page.component';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule, LOCALE_ID } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NvD3Module } from 'ng2-nvd3';

import { BootstrapModalModule } from 'ngx-modialog/plugins/bootstrap/src/ngx-modialog-bootstrap.ng-flat';
import { ModalModule } from 'ngx-modialog';
// import { CurrencyMaskModule } from 'ng2-currency-mask';
import { ToastyModule } from 'ng2-toasty';
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
import { MyCurrencyFormatterDirective } from './directives/currency-formatter.directive';

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
    TableroTallerComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule,
    ModalModule.forRoot(),
    ToastyModule.forRoot(),
    DpDatePickerModule,
    BootstrapModalModule,
    APP_ROUTING,
    BrowserAnimationsModule,
    NvD3Module,
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
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
