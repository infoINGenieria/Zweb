import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AlquiladosDetailComponent } from './alquilados-detail.component';

describe('AlquiladosDetailComponent', () => {
  let component: AlquiladosDetailComponent;
  let fixture: ComponentFixture<AlquiladosDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AlquiladosDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AlquiladosDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
