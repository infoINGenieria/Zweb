import { MenuEntry } from './../../models/Interfaces';
import { Observable } from 'rxjs/Observable';
import { Injectable } from '@angular/core';
import {Http, Headers, RequestOptions} from '@angular/http';

@Injectable()
export class BaseApiService {

  constructor(private http: Http) {
  }

  get xsrfToken() {
    const name = 'csrftoken';
    let value = '; ' + document.cookie;
    let parts = value.split('; ' + name + '=');
    if (parts.length === 2) {
       return parts.pop().split(';').shift();
    }
  }

  private getRequestOptions() {
    const headers = new Headers({'Content-Type': 'application/json', 'X-CSRFToken': this.xsrfToken});
    return new RequestOptions({headers: headers});
  }

  get(url) {
    return this.http.get(url, this.getRequestOptions())
      .catch(error => error.json());
  }

  post(url, payload) {
    return this.http.post(url, payload, this.getRequestOptions())
      .catch(error => error.json());
  }

  put(url, payload) {
    return this.http.put(url, payload, this.getRequestOptions())
      .catch(error => error.json());
  }
  delete(url) {
    return this.http.delete(url, this.getRequestOptions())
      .catch(error => error.json());
  }

  /*   Common methods API */

  get_my_menu(): Observable<any> {
    return this.get('/api/my_menu/')
      .map((r: Response) => r.json());
  }
}
