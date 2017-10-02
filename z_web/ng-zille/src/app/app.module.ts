import { BrowserModule } from '@angular/platform-browser';
import { NgModule, LOCALE_ID } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';

import { BootstrapModalModule } from 'ngx-modialog/plugins/bootstrap';
import { ModalModule } from 'ngx-modialog';
// import { CurrencyMaskModule } from 'ng2-currency-mask';

import { APP_ROUTING } from './app.routes';

// Services
import { CoreService } from './services/core/core.service';
import { BaseApiService } from './services/base-api/base-api.service';

// Own
import { AppComponent } from './app.component';
import { PresupuestoComponent } from './components/presupuesto/presupuesto.component';
import { PresupuestosComponent } from './components/presupuestos/presupuestos.component';
import { PresupuestosService } from './services/presupuestos/presupuestos.service';
import { TipoItemPresupuestoComponent } from './components/tipo-item-presupuesto/tipo-item-presupuesto.component';
import { IndexComponent } from './components/index/index.component';

@NgModule({
  declarations: [
    AppComponent,
    PresupuestosComponent,
    PresupuestoComponent,
    TipoItemPresupuestoComponent,
    IndexComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule,
    ModalModule.forRoot(),
    BootstrapModalModule,
    APP_ROUTING,
    // CurrencyMaskModule
  ],
  providers: [
    {provide: LOCALE_ID, useValue: 'es-AR'},
    BaseApiService,
    PresupuestosService,
    CoreService,
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
