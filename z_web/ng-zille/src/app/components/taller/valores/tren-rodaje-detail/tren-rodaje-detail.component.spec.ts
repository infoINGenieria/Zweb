import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TrenRodajeDetailComponent } from './tren-rodaje-detail.component';

describe('TrenRodajeDetailComponent', () => {
  let component: TrenRodajeDetailComponent;
  let fixture: ComponentFixture<TrenRodajeDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TrenRodajeDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TrenRodajeDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
