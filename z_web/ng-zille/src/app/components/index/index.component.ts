import { fadeInAnimation } from './../../_animations/index';
import { Component, OnInit } from '@angular/core';
import { MenuEntry } from '../../models/Interfaces';
import { BaseApiService } from '../../services/base-api/base-api.service';

@Component({
  selector: 'app-index',
  templateUrl: './index.component.html',
  styleUrls: ['./index.component.css'],
  // make fade in animation available to this component
  animations: [fadeInAnimation],
})
export class IndexComponent implements OnInit {

  menu: MenuEntry[] = [];

  constructor(private _service: BaseApiService) {
  }

  ngOnInit() {
    this._service.get_my_menu().subscribe(menu => {
      this.menu = menu;
      }
    );
  }

  get_link(url: String) {
    return url.substr(2);  // remove duplicate ~/
  }
}
