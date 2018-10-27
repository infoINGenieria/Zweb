import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ParametrosGralComponent } from './parametros-gral.component';

describe('ParametrosGralComponent', () => {
  let component: ParametrosGralComponent;
  let fixture: ComponentFixture<ParametrosGralComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ParametrosGralComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ParametrosGralComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
