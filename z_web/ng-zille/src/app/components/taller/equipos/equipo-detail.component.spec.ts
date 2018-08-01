import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EquipoDetailComponent } from './equipo-detail.component';

describe('EquipoDetailComponent', () => {
  let component: EquipoDetailComponent;
  let fixture: ComponentFixture<EquipoDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EquipoDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EquipoDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
