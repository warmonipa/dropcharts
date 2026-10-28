import {ApplicationConfig, provideZonelessChangeDetection} from '@angular/core';
import {provideClientHydration, withEventReplay} from '@angular/platform-browser';
import {provideRouter, withInMemoryScrolling, UrlSerializer} from '@angular/router';
import {PublicUrlSerializer} from './public-url-serializer';
import {routes} from './app.routes';
export const appConfig: ApplicationConfig = {
  providers: [{provide: UrlSerializer, useClass: PublicUrlSerializer}, provideZonelessChangeDetection(), provideClientHydration(withEventReplay()),
    provideRouter(routes, withInMemoryScrolling({scrollPositionRestoration: 'enabled'}))],
};
