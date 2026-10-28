import {Component} from '@angular/core';
import {RouterLink} from '@angular/router';
@Component({selector: 'drop-not-found', imports: [RouterLink], template: '<main class="content"><h1>Page not found</h1><a routerLink="/">PSO Drop Charts</a></main>'})
export class NotFoundComponent {}
