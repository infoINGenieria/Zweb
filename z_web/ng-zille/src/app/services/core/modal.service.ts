import { NgxSmartModalService, NgxSmartModalComponent } from 'ngx-smart-modal';
import { Injectable } from '@angular/core';


@Injectable()
export class ModalService {

    modal: NgxSmartModalComponent;

    constructor(
        public ngxSmartModalService: NgxSmartModalService
    ) {  }

    executeOkAndClose(callback) {
        callback();
        this.modal.close();
    }

    reset(modal) {
        modal.removeData();
    }
    setUp(
        message: string, title = 'Atención',
        okCallback = null, okText = 'OK',
        cancelCallback = null, cancelText = 'Cancelar'
        ) {
        this.modal = this.ngxSmartModalService.getModal('myModal');
        this.modal.onClose.subscribe(modal => this.reset(modal));

        let data: any = {
            title: title,
            message: message,
            cancelText: cancelText
        };
        if (okCallback) {
            data.okCallback = () => this.executeOkAndClose(okCallback);
            data.okText = okText;
        }
        if (cancelCallback) {
            data.cancelCallback = cancelCallback;
        } else {
            data.cancelCallback = () => this.modal.close();
        }
        this.modal.setData(data);
        return this.modal;
    }
}
