import {afterNextRender, DestroyRef, Directive, ElementRef, inject} from '@angular/core';

@Directive({selector: '[tableViewport]'})
export class TableViewportDirective {
  constructor() {
    const wrap = inject(ElementRef<HTMLElement>).nativeElement;
    const destroy = inject(DestroyRef);
    afterNextRender(() => {
      const center = () => wrap.style.setProperty('--area-label-center', Math.round(wrap.clientWidth / 2) + 'px');
      const observer = new ResizeObserver(center);
      observer.observe(wrap);
      center();
      destroy.onDestroy(() => observer.disconnect());
    });
  }
}
