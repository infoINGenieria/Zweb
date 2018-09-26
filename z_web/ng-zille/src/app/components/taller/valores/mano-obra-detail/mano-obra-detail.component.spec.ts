import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ManoObraDetailComponent } from './mano-obra-detail.component';

describe('ManoObraDetailComponent', () => {
  let component: ManoObraDetailComponent;
  let fixture: ComponentFixture<ManoObraDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ManoObraDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ManoObraDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
