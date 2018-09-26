import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ReparacionesDetailComponent } from './reparaciones-detail.component';

describe('ReparacionesDetailComponent', () => {
  let component: ReparacionesDetailComponent;
  let fixture: ComponentFixture<ReparacionesDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ReparacionesDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ReparacionesDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
