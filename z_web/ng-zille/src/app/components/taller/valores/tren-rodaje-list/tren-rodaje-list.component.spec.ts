import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TrenRodajeListComponent } from './tren-rodaje-list.component';

describe('TrenRodajeListComponent', () => {
  let component: TrenRodajeListComponent;
  let fixture: ComponentFixture<TrenRodajeListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TrenRodajeListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TrenRodajeListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
