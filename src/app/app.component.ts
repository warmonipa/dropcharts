import {Component, inject} from '@angular/core';
import {DOCUMENT} from '@angular/common';
import {NavigationEnd, Router, RouterOutlet} from '@angular/router';
import {takeUntilDestroyed} from '@angular/core/rxjs-interop';
@Component({selector: 'drop-app', imports: [RouterOutlet], template: '<router-outlet />'})
export class AppComponent {
  constructor() {
    const document = inject(DOCUMENT);
    inject(Router).events.pipe(takeUntilDestroyed()).subscribe(event => {
      if (!(event instanceof NavigationEnd)) return;
      const canonical = document.querySelector<HTMLLinkElement>('link[rel="canonical"]') || document.createElement('link');
      canonical.rel = 'canonical';
      canonical.href = 'https://dropcharts.psohaven.com' + event.urlAfterRedirects.split(/[?#]/)[0];
      document.head.appendChild(canonical);
    });
  }
}
