import {afterNextRender, Component, computed, DestroyRef, effect, inject, signal} from '@angular/core';
import {DOCUMENT} from '@angular/common';
import {Title} from '@angular/platform-browser';
import {ActivatedRoute, Params, Router, RouterLink} from '@angular/router';
import {takeUntilDestroyed, toSignal} from '@angular/core/rxjs-interop';
import {buildChart, Bundle, ChartState, episodes, languages, readState, stateParams} from './chart-model';
import messages from './messages.json';
import images from '../../../shared/images/mapping.json';
import {TableViewportDirective} from './table-viewport.directive';
import {PreviewComponent} from './preview.component';

@Component({
  selector: 'drop-chart',
  imports: [RouterLink, TableViewportDirective, PreviewComponent],
  templateUrl: './chart.component.html',
})
export class ChartComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly document = inject(DOCUMENT);
  private readonly title = inject(Title);
  private readonly routeData = toSignal(this.route.data, {initialValue: this.route.snapshot.data});
  // Static HTML has the default chart. Hydrate that tree before applying URL filters.
  private readonly query = signal<Params>({});
  readonly bundle = computed(() => this.routeData()['bundle'] as Bundle);
  readonly state = computed(() => readState(this.bundle(), this.query()));
  readonly text = computed<Record<string, string>>(() => messages[this.bundle().version][this.state().lang]);
  readonly chart = computed(() => buildChart(this.bundle(), this.state(), this.text(), images));
  readonly episodes = computed(() => ['all', ...episodes(this.bundle())]);
  readonly difficulties = computed(() => Object.keys(this.bundle().languages.en.data));
  readonly languages = languages;
  readonly languageNames = {en: 'EN', ja: '日本語', zh: '中文'};
  constructor() {
    const destroy = inject(DestroyRef);
    afterNextRender(() => {
      this.route.queryParams.pipe(takeUntilDestroyed(destroy)).subscribe(params => {
        this.query.set(params);
        const canonical = stateParams(readState(this.bundle(), params));
        if (Object.entries(canonical).some(([key, value]) => (params[key] || null) !== value)) {
          void this.router.navigate([], {relativeTo: this.route, queryParams: canonical, queryParamsHandling: 'merge', preserveFragment: true, replaceUrl: true});
        }
      });
    });
    effect(() => {
      this.document.documentElement.lang = this.state().lang;
      this.title.setTitle(this.text().title);
    });
  }
  set(key: keyof ChartState, value: string) {
    void this.router.navigate([], {relativeTo: this.route, queryParams: {[key]: value || null}, queryParamsHandling: 'merge', preserveFragment: true, replaceUrl: true});
  }
}
