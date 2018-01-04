import { BrowserModule } from '@angular/platform-browser';
import { NgModule, LOCALE_ID } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NvD3Module } from 'ng2-nvd3';

import { BootstrapModalModule } from 'ngx-modialog/plugins/bootstrap';
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

// d3 and nvd3 should be included somewhere
import 'd3';
import 'nvd3';

// pipe
import { MonedaPipe } from './pipes/moneda.pipe';
import { PorcientoPipe } from './pipes/porciento.pipe';
import { MyCurrencyPipe } from './pipes/my-currency.pipe';
import { MyCurrencyFormatterDirective } from './directives/currency-formatter.directive';


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
    MyCurrencyPipe,
    MyCurrencyFormatterDirective,
    PorcientoPipe,
    AvanceObraComponent
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
    ProyeccionesService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
