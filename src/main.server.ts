import {BootstrapContext, bootstrapApplication} from '@angular/platform-browser';
import {mergeApplicationConfig} from '@angular/core';
import {provideServerRendering, RenderMode, withRoutes} from '@angular/ssr';
import {AppComponent} from './app/app.component';
import {appConfig} from './app/app.config';
import {platforms} from './app/platforms';
export default (context: BootstrapContext) => bootstrapApplication(AppComponent, mergeApplicationConfig(appConfig, {
  providers: [provideServerRendering(withRoutes([
    ...['', ...platforms.map(p => p.path), '404'].map(path => ({path, renderMode: RenderMode.Prerender as const})),
    {path: '**', renderMode: RenderMode.Client},
  ]))],
}), context);
