import { Directive, HostListener, ElementRef, OnInit } from '@angular/core';
import { MyCurrencyPipe } from '../pipes/my-currency.pipe';

@Directive({ selector: '[myCurrencyFormatter]' })
export class MyCurrencyFormatterDirective implements OnInit {

  private el: any;

  constructor(
    private elementRef: ElementRef,
  ) {
    this.el = this.elementRef.nativeElement;
  }

  ngOnInit() {  }

  @HostListener('keyup', ['$event.target.value'])
  onKeyUp(value) {
     let val = value.replace(',', '.');
     if ((val.match(/\./g) || []).length > 1) {
       val = val.substr(0, val.length - 1);
     }
     this.el.value = val;
  }

}
