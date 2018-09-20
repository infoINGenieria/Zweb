import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TableroTallerComponent } from './tablero-taller.component';

describe('TableroTallerComponent', () => {
  let component: TableroTallerComponent;
  let fixture: ComponentFixture<TableroTallerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TableroTallerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TableroTallerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
