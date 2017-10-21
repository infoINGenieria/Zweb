import { RegistroService } from './services/registro/registro.service';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule, LOCALE_ID } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

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
import { NotificationService } from './services/core/notifications.service';

// Own
import { AppComponent } from './app.component';
import { PresupuestoComponent } from './components/presupuesto/presupuesto.component';
import { PresupuestosComponent } from './components/presupuestos/presupuestos.component';
import { PresupuestosService } from './services/presupuestos/presupuestos.service';
import { TipoItemPresupuestoComponent } from './components/tipo-item-presupuesto/tipo-item-presupuesto.component';
import {
  CertificacionesIndexComponent, CertificacionesRealComponent, CertificacionRealComponent,
  CertificacionesProyeccionComponent, CertificacionProyeccionComponent } from './components/certificaciones';
import { IndexComponent } from './components/index/index.component';

@NgModule({
  declarations: [
    AppComponent,
    PresupuestosComponent,
    PresupuestoComponent,
    TipoItemPresupuestoComponent,
    IndexComponent,
    CertificacionesRealComponent,
    CertificacionRealComponent,
    CertificacionesProyeccionComponent,
    CertificacionesIndexComponent,
    CertificacionProyeccionComponent
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
    // CurrencyMaskModule
  ],
  providers: [
    {provide: LOCALE_ID, useValue: 'es-AR'},
    BaseApiService,
    PresupuestosService,
    CoreService,
    NotificationService,
    RegistroService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
