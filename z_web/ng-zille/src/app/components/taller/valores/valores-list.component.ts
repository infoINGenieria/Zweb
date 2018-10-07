import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-valores-list',
  templateUrl: './valores-list.component.html',
  styleUrls: ['./valores-list.component.scss']
})
export class ValoresListComponent implements OnInit {

  tabName: string;
  constructor(
    private router: Router,
  ) { }

  ngOnInit() {
    this.changeTab('lubricantes');

  }

  changeTab(name) {
    this.tabName = name;
    this.router.navigate(['/taller/valores', {
      outlets: {
        'tabs': [this.tabName],
        'details': []
      }
    }]
    );
  }
}
