import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ReparacionesListComponent } from './reparaciones-list.component';

describe('ReparacionesListComponent', () => {
  let component: ReparacionesListComponent;
  let fixture: ComponentFixture<ReparacionesListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ReparacionesListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ReparacionesListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
