import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PosesionDetailComponent } from './posesion-detail.component';

describe('PosesionDetailComponent', () => {
  let component: PosesionDetailComponent;
  let fixture: ComponentFixture<PosesionDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PosesionDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PosesionDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
