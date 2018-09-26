import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PosesionListComponent } from './posesion-list.component';

describe('PosesionListComponent', () => {
  let component: PosesionListComponent;
  let fixture: ComponentFixture<PosesionListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PosesionListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PosesionListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
