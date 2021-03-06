import { Injectable } from '@angular/core';
import {ToastaService, ToastaConfig, ToastOptions } from 'ngx-toasta';

@Injectable()
export class NotificationService {

  constructor(private toastyService: ToastaService, private toastyConfig: ToastaConfig) {
    this.toastyConfig.theme = 'bootstrap';
    this.toastyConfig.showClose = true;
    this.toastyConfig.timeout = 5000;
  }

  showNotification(msg: string, title: string, type: string = 'success') {
    const toastOptions: ToastOptions = {
      title: title,
      msg: msg
    };

    switch (type) {
      case 'success':
        this.toastyService.success(toastOptions);
        break;
      case 'info':
        this.toastyService.info(toastOptions);
        break;
      case 'warning':
        this.toastyService.warning(toastOptions);
        break;
      case 'error':
        this.toastyService.error(toastOptions);
        break;
      default:
      this.toastyService.default(toastOptions);
    }
  }

  // shortcuts
  success(msg: string, title = 'Éxito') {
    this.showNotification(msg, title, 'success');
  }

  error(msg: string, title = 'Error') {
    this.showNotification(msg, title, 'error');
  }

  info(msg: string, title = 'Información') {
    this.showNotification(msg, title, 'info');
  }

  warning(msg: string, title = 'Advertencia') {
    this.showNotification(msg, title, 'warning');
  }

}
