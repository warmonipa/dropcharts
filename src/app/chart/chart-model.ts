import {areaFor} from './areas.ts';

export type Version = 'bb' | 'dc' | 'ngc';
export type Language = 'en' | 'ja' | 'zh';
export interface Drop {item: string; rate: string; ss?: boolean; bannerHit?: number}
export type Cell = Drop | {items: Drop[]};
export interface Entry {name: string; dropRate?: string; drops: Cell[]}
export interface Dataset {
  sectionIds: string[];
  sectionColors: string[];
  data: Record<string, Record<string, Record<string, Entry[]>>>;
}
interface Variant {names: Record<Language, string>; image?: string | null; source?: string | null}
export interface Profile {id: string; normal: Variant; ultimate: Variant}
export interface Bundle {
  version: Version;
  languages: Record<Language, Dataset>;
  monsters: Record<string, Record<string, Profile>>;
  items: Record<string, string>;
}
export interface ChartState {lang: Language; diff: string; type: string; ep: string; rate: string; q: string}
export const languages: Language[] = ['en', 'ja', 'zh'];
export const sectionIcons = ['Viridia', 'Greenill', 'Skyly', 'Bluefull', 'Purplenum', 'Pinkal', 'Redria', 'Oran', 'Yellowboze', 'Whitill'];
const sectionText: Record<string, string> = {
  '#00A562': '#fff', '#76FE43': '#000', '#59F9F9': '#000', '#4488FF': '#fff', '#CC00FF': '#fff',
  '#FF87CB': '#000', '#F70F0F': '#fff', '#F7830F': '#000', '#F7F715': '#000', '#FFFFFF': '#000',
};
export const cellDrops = (cell: Cell): Drop[] => 'items' in cell ? cell.items : [cell];
export function episodes(bundle: Bundle): string[] {
  return Object.keys(bundle.languages.en.data['Normal']['monsters']);
}
export function readState(bundle: Bundle, params: Record<string, string>): ChartState {
  return {
    lang: languages.includes(params['lang'] as Language) ? params['lang'] as Language : 'en',
    diff: Object.keys(bundle.languages.en.data).includes(params['diff']) ? params['diff'] : 'Normal',
    type: bundle.version === 'bb' && params['type'] === 'boxes' ? 'boxes' : 'monsters',
    ep: bundle.version !== 'dc' && episodes(bundle).includes(params['ep']) ? params['ep'] : 'all',
    rate: bundle.version === 'bb' && params['rate'] === 'fraction' ? 'fraction' : 'percent',
    q: params['q'] || '',
  };
}
export function stateParams(state: ChartState): Record<string, string | null> {
  return {lang: state.lang === 'en' ? null : state.lang, diff: state.diff === 'Normal' ? null : state.diff,
    type: state.type === 'monsters' ? null : state.type, ep: state.ep === 'all' ? null : state.ep,
    rate: state.rate === 'percent' ? null : state.rate, q: state.q || null};
}
export function fuzzyMatch(text: string, term: string): boolean {
  text = text.normalize('NFKC').toLowerCase();
  term = term.normalize('NFKC').toLowerCase();
  let offset = 0;
  for (const char of term) {
    offset = text.indexOf(char, offset);
    if (offset === -1) return false;
    offset++;
  }
  return true;
}
export function parseRate(raw = ''): number {
  if (raw.endsWith('%')) return parseFloat(raw) / 100;
  const parts = raw.split('/');
  return parts.length === 2 ? parseFloat(parts[0]) / parseFloat(parts[1]) : NaN;
}
function percent(probability: number): string {
  const value = probability * 100;
  if (value >= 100) return '100%';
  return value.toFixed(value >= 10 ? 1 : value >= 1 ? 2 : value >= 0.1 ? 3 : 4) + '%';
}
export function formatRate(raw: string, version: Version, format: string): string {
  if (version === 'bb') return format === 'fraction' || !raw.includes('/') ? raw : percent(parseRate(raw));
  const match = /^([<>]?)(\d+(?:\.\d+)?)%$/.exec(raw);
  if (!match || !parseFloat(match[2])) return raw;
  let digits = parseFloat(match[2]).toPrecision(3);
  if (digits.includes('e')) return raw;
  if (digits.includes('.')) digits = digits.replace(/0+$/, '').replace(/\.$/, '');
  return match[1] + digits + '%';
}
export function dropRate(drop: Drop, entry: Entry, version: Version, state: ChartState) {
  let raw = drop.rate;
  let tooltip = '';
  if (raw && version === 'dc') {
    raw = (parseRate(raw) * parseRate(entry.dropRate) * 100).toFixed(12).replace(/0+$/, '').replace(/\.$/, '') + '%';
    tooltip = 'RDR = ' + formatRate(drop.rate, version, state.rate);
  } else if (raw && state.type === 'monsters') {
    const dr = parseRate(raw), dar = parseRate(entry.dropRate), rdr = dr / dar;
    if (Number.isFinite(rdr) && dr > 0 && dar > 0 && rdr <= 1.000001) {
      tooltip = 'RDR ≈ ' + (version === 'bb' && state.rate === 'fraction'
        ? '1/' + Math.round(1 / Math.min(rdr, 1) * 10) / 10 : percent(Math.min(rdr, 1)));
    }
  }
  return {rate: formatRate(raw, version, state.rate), tooltip};
}
function havenLink(kind: string, id: string, state: ChartState): string {
  const prefix = state.lang === 'zh' ? '' : `/${state.lang}`;
  const difficulty: Record<string, string> = {Normal: 'n', Hard: 'h', 'Very Hard': 'vh', Ultimate: 'u'};
  return `https://www.psohaven.com${prefix}/${kind}/${id}/` + (kind === 'enemies' ? `?diff=${difficulty[state.diff]}` : '');
}
export function buildChart(bundle: Bundle, state: ChartState, messages: Record<string, string>, images: Record<string, string>) {
  const data = bundle.languages[state.lang], en = bundle.languages.en;
  const sections = data.sectionIds.map((name, i) => ({name, color: data.sectionColors[i], text: sectionText[data.sectionColors[i].toUpperCase()], icon: sectionIcons[i]}));
  const source = data.data[state.diff][state.type] || {};
  const term = state.q.trim();
  let total = 0, shown = 0;
  const tables = (state.ep === 'all' ? Object.keys(source) : [state.ep]).flatMap(ep => {
    const entries = source[ep] || [];
    total += entries.length;
    let lastArea: string | null = null;
    const rows = entries.flatMap((entry, index) => {
      const english = en.data[state.diff][state.type][ep][index];
      const profile = bundle.version === 'bb' && state.type === 'monsters' ? bundle.monsters[ep][english.name] : null;
      const names = profile ? [...Object.values(profile.normal.names), ...Object.values(profile.ultimate.names)] : [entry.name];
      if (term && !names.some(name => fuzzyMatch(name, term)) && !entry.drops.some(cell => cellDrops(cell).some(drop => drop.item && fuzzyMatch(drop.item, term)))) return [];
      const variant = profile ? profile[state.diff === 'Ultimate' ? 'ultimate' : 'normal'] : null;
      const area = state.type === 'monsters' ? areaFor(ep, english.name) : null;
      const heading = area !== lastArea ? area : null;
      const firstArea = lastArea === null;
      lastArea = area;
      const cells = entry.drops.map((cell, column) => {
        const drops = cellDrops(cell).flatMap((drop, dropIndex) => {
          if (!drop.item) return [];
          const enItem = cellDrops(english.drops[column])[dropIndex].item;
          const hit = bundle.version === 'bb' && Number.isInteger(drop.bannerHit) && (drop.bannerHit || 0) > 0;
          const hint = hit ? messages['bannerHitHint'].replace('{hit}', String(drop.bannerHit)) : bundle.version === 'bb' && drop.ss ? messages['bannerNoHitHint'] : '';
          const image = images[drop.item] || images[enItem];
          return [{name: drop.item, ...dropRate(drop, entry, bundle.version, state),
            href: bundle.version === 'bb' ? havenLink('items', bundle.items[enItem], state) : null,
            image: image ? '/shared/images/' + encodeURIComponent(image) : null,
            rare: !!drop.ss, hit: !!hit, hint, highlight: !!term && fuzzyMatch(drop.item, term)}];
        });
        return {drops, rare: drops.some(drop => drop.rare), ...sections[column]};
      });
      return [{index, heading, firstArea, name: variant ? variant.names[state.lang] : entry.name.replaceAll('/', '\n'),
        href: profile ? havenLink('enemies', profile.id, state) : null,
        image: variant?.image ? '/bb/images/monsters/' + variant.image : null,
        dar: formatRate(entry.dropRate || '', bundle.version, state.rate), cells}];
    });
    shown += rows.length;
    return rows.length ? [{ep, label: ep + (state.type === 'boxes' ? ' - ' + messages['boxes'] : ''), rows}] : [];
  });
  const stats = term ? messages['showing'].replace('{shown}', String(shown)).replace('{total}', String(total)).replace('{term}', term.toLowerCase())
    : messages['entries'].replace('{diff}', state.diff).replace('{total}', String(total));
  return {sections, tables, total, shown, stats};
}
