import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AsistenciaFormComponent } from './asistencia-form.component';

describe('AsistenciaFormComponent', () => {
  let component: AsistenciaFormComponent;
  let fixture: ComponentFixture<AsistenciaFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AsistenciaFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AsistenciaFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
