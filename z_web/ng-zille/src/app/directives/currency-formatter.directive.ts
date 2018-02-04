import { Directive, HostListener, ElementRef, OnInit} from '@angular/core';

@Directive({ selector: '[appMyCurrencyFormatter]' })
export class MyCurrencyFormatterDirective implements OnInit {

  private el: any;

  constructor(
    private elementRef: ElementRef,
  ) {
    this.el = this.elementRef.nativeElement;
  }

  ngOnInit() {
    // this.el.value = this.currencyPipe.transform(this.el.value);
    }

  @HostListener('keyup', ['$event.target.value'])
  onKeyUp(value) {
    let val = value.replace(',', '.');
    this.el.value = val;
  }

  // @HostListener('focus', ['$event.target.value'])
  // onFocus(value) {
  //   console.log("focus");
  //   this.el.value = this.currencyPipe.parse(value); // opossite of transform
  // }

  // @HostListener('blur', ['$event.target.value'])
  // onBlur(value) {
  //   console.log("blur");
  //   this.el.value = this.currencyPipe.transform(value);
  // }

}
