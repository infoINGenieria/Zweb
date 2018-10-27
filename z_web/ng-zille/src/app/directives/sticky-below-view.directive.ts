import { Directive, ElementRef, Renderer2, HostListener } from '@angular/core';


enum StickyState {
  fixed =  'fixed',
  noFixed =  'no-fixed'
}

@Directive({
  selector: '[appStickyBelowView]'
})
export class StickyBelowViewDirective {
  private initialOffsetFromTop =  0;

  private fixedState = StickyState.noFixed;
  private fixedViewportOffset = 0;

  constructor(
      private element: ElementRef,
      private renderer: Renderer2
    ) {
        this.getInitialOffset();
        this.getFixedViewportOffset();
        console.log('directive', this.initialOffsetFromTop, this.fixedState, this.fixedViewportOffset);
      }

    private getInitialOffset() {
      const initialViewportOffset = this.element.nativeElement.getBoundingClientRect().top;
      const currentScroll = window.scrollY;
      this.initialOffsetFromTop = initialViewportOffset + currentScroll;
    }

    private getFixedViewportOffset(){
      // set the fixed class
      this.renderer.addClass(this.element.nativeElement, 'fixed');
      // save the view offset in fixed position
      this.fixedViewportOffset = this.element.nativeElement.getBoundingClientRect().top;
      // remove again the fixed class
      this.renderer.removeClass(this.element.nativeElement, 'fixed');
    }

  @HostListener('window:scroll', ['$event'])
  private handleScroll($event: Event) {
    console.log($event);
    const currentScroll = $event.srcElement.children[0].scrollTop;

    // if not fixed
    // and we have not yet scrolled until the original position of the element
    // add the fixed class
    if (this.fixedState == StickyState.noFixed &&
        currentScroll + this.fixedViewportOffset < this.initialOffsetFromTop) {
        this.fixedState = StickyState.fixed;
        this.renderer.addClass(this.element.nativeElement, 'fixed');
    } else {  // if fixed
      if (this.fixedState == StickyState.fixed) {
        const currentOffsetFromTop = currentScroll + this.element.nativeElement.getBoundingClientRect().top;
        // and the current offset from top is greater or equal than the original
        // remove the fixed class
        if (currentOffsetFromTop >= this.initialOffsetFromTop) {
          this.fixedState = StickyState.noFixed;
          this.renderer.removeClass(this.element.nativeElement, 'fixed');
        }
      }
    }
  }
}
