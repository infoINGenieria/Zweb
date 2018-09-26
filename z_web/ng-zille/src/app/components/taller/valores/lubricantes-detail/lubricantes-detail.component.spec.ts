import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { LubricantesDetailComponent } from './lubricantes-detail.component';

describe('LubricantesDetailComponent', () => {
  let component: LubricantesDetailComponent;
  let fixture: ComponentFixture<LubricantesDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LubricantesDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LubricantesDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
