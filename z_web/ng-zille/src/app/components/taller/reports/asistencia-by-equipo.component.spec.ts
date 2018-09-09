import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AsistenciaByEquipoComponent } from './asistencia-by-equipo.component';

describe('AsistenciaByEquipoComponent', () => {
  let component: AsistenciaByEquipoComponent;
  let fixture: ComponentFixture<AsistenciaByEquipoComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AsistenciaByEquipoComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AsistenciaByEquipoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
