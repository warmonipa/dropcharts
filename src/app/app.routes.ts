import {inject} from '@angular/core';
import {Route, Router, Routes} from '@angular/router';
import type {Bundle} from './chart/chart-model';
import {platforms} from './platforms';
export const routes: Routes = [
  // Existing static index documents remain valid HTTP entry points.
  {matcher: segments => segments.at(-1)?.path === 'index.html' && segments.length <= 2 ? {consumed: segments} : null,
    redirectTo: ({url, queryParams, fragment}) => inject(Router).createUrlTree(
      ['/' + url.slice(0, -1).map(s => s.path).join('/')], {queryParams, fragment: fragment ?? undefined}),
  },
  {path: '', pathMatch: 'full', title: 'PSO Drop Charts', loadComponent: () => import('./home.component').then(m => m.HomeComponent)},
  ...platforms.map(({version, path}) => ({
    path,
    loadComponent: () => import('./chart/chart.component').then(m => m.ChartComponent),
    resolve: {bundle: async (): Promise<Bundle> => {
      switch (version) {
        case 'bb': return (await import('./generated/bb.json')).default as Bundle;
        case 'dc': return (await import('./generated/dc.json')).default as Bundle;
        case 'ngc': return (await import('./generated/ngc.json')).default as Bundle;
      }
    }},
  })),
  ...platforms.map<Route>(({version, path}) => ({
    path: version, pathMatch: 'full',
    redirectTo: ({queryParams, fragment}) =>
      inject(Router).createUrlTree(['/' + path], {queryParams, fragment: fragment ?? undefined}),
  })),
  {path: '404', title: 'Page not found | PSO Drop Charts', loadComponent: () => import('./not-found.component').then(m => m.NotFoundComponent)},
  {path: '**', loadComponent: () => import('./not-found.component').then(m => m.NotFoundComponent)},
];
