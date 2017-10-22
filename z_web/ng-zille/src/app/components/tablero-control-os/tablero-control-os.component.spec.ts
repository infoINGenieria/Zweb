import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TableroControlOsComponent } from './tablero-control-os.component';

describe('TableroControlOsComponent', () => {
  let component: TableroControlOsComponent;
  let fixture: ComponentFixture<TableroControlOsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TableroControlOsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TableroControlOsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
