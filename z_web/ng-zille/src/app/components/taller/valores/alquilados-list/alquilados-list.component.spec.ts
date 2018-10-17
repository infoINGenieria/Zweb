import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AlquiladosListComponent } from './alquilados-list.component';

describe('AlquiladosListComponent', () => {
  let component: AlquiladosListComponent;
  let fixture: ComponentFixture<AlquiladosListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AlquiladosListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AlquiladosListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
