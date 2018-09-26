import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ManoObraListComponent } from './mano-obra-list.component';

describe('ManoObraListComponent', () => {
  let component: ManoObraListComponent;
  let fixture: ComponentFixture<ManoObraListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ManoObraListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ManoObraListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
