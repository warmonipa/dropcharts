import {Component, inject} from '@angular/core';
import {DOCUMENT} from '@angular/common';
import {RouterLink} from '@angular/router';
@Component({selector: 'drop-home', imports: [RouterLink], templateUrl: './home.component.html', styleUrl: './home.component.css'})
export class HomeComponent {constructor() {inject(DOCUMENT).documentElement.lang = 'en';}}
