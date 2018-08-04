import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ParametrosGralPageComponent } from './parametros-gral-page.component';

describe('ParametrosGralPageComponent', () => {
  let component: ParametrosGralPageComponent;
  let fixture: ComponentFixture<ParametrosGralPageComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ParametrosGralPageComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ParametrosGralPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
