import { map } from 'rxjs/operators';
import { Observable } from 'rxjs/Rx';
import { Injectable } from '@angular/core';
import {Http, Headers, RequestOptions, Response, URLSearchParams } from '@angular/http';

import { environment } from '../../../environments/environment';

import { MenuEntry } from '../../models/Interfaces';

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

  private getRequestOptions(params?: URLSearchParams, headers?: Headers, options?: any) {
    let _headers = new Headers();
    if (headers) {
      _headers = headers;
    }
    _headers.append('Content-Type', 'application/json');
    _headers.append('X-CSRFToken', this.xsrfToken);

    let _options = new RequestOptions({headers: _headers});
    if (params) {
      _options.merge({'params': params});
    }
    if (options) {
      _options.merge(options);
    }
    return _options;
  }

  get(url, params?: URLSearchParams, headers?: Headers, options?: any): Observable<Response> {
    return this.http.get(`${environment.apiUrl}${url}`, this.getRequestOptions(params, headers, options));
  }

  post(url, payload): Observable<Response> {
    return this.http.post(`${environment.apiUrl}${url}`, payload, this.getRequestOptions());
  }

  put(url, payload): Observable<Response> {
    return this.http.put(`${environment.apiUrl}${url}`, payload, this.getRequestOptions());
  }
  delete(url): Observable<Response> {
    return this.http.delete(`${environment.apiUrl}${url}`, this.getRequestOptions());
  }

  /*   Common methods API */

  get_my_menu(): Observable<MenuEntry[]> {
    return this.get(`${environment.apiUrl}/api/my_menu/`).pipe(
      map((r: Response) => r.json())
    );
  }
}
