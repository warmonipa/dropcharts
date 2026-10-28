import {Component, effect, input, signal} from '@angular/core';

@Component({
  selector: 'drop-preview',
  template: `<ng-content />
    @if (preview(); as value) {
      @if (value.image) {<img id="item-tooltip" [src]="value.image" alt="" [style.left.px]="value.x" [style.top.px]="value.y" style="display:block" (mouseenter)="keep()" (mouseleave)="hideSoon()">}
      @else {<div id="rate-tooltip" role="tooltip" [style.left.px]="value.x" [style.top.px]="value.y" style="display:block">{{value.text}}</div>}
    }`,
  host: {'(mousemove)': 'show($event)', '(focusin)': 'focus($event)', '(focusout)': 'close()',
    '(mouseleave)': 'hideSoon()', '(document:keydown.escape)': 'dismiss()', '(window:scroll)': 'close()', '(scroll)': 'close()'},
})
export class PreviewComponent {
  readonly context = input.required<unknown>();
  readonly preview = signal<{image?: string; text?: string; x: number; y: number} | null>(null);
  private active: Element | null = null;
  private dismissed: Element | null = null;
  private timer?: ReturnType<typeof setTimeout>;
  constructor() {effect(() => {this.context(); this.close();});}
  ngOnDestroy() {clearTimeout(this.timer);}
  keep() {clearTimeout(this.timer); this.timer = undefined;}
  close() {this.keep(); this.preview.set(null); this.active = null;}
  dismiss() {this.dismissed = this.active; this.close();}
  hideSoon() {if (!this.timer) this.timer = setTimeout(() => this.close(), 120);}
  focus(event: FocusEvent) {
    const target = event.target as HTMLElement;
    const rect = target.getBoundingClientRect();
    this.showAt(target, rect.right, rect.bottom);
  }
  show(event: MouseEvent) {this.showAt(event.target as HTMLElement, event.clientX, event.clientY);}
  private showAt(target: HTMLElement, x: number, y: number) {
    if (target.id === 'item-tooltip') {this.keep(); return;}
    const element = target.closest<HTMLElement>('[data-rdr], [data-preview]');
    if (element !== this.dismissed) this.dismissed = null;
    if (!element || element === this.dismissed) {this.hideSoon(); return;}
    this.keep();
    if (element === this.active && this.preview()) return;
    this.active = element;
    const image = element.dataset['preview'], text = element.dataset['rdr'];
    const width = image ? 90 : 230;
    this.preview.set({image, text, x: Math.max(4, Math.min(x + 12, window.innerWidth - width - 4)),
      y: Math.max(4, Math.min(y > 100 && image ? y - 90 : y + 16, window.innerHeight - (image ? 90 : 48)))});
  }
}
