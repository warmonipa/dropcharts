import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {buildChart, readState, stateParams, cellDrops, fuzzyMatch, formatRate} from '../src/app/chart/chart-model.ts';
import {areaFor} from '../src/app/chart/areas.ts';
import {reviewedAreas} from './reviewed-areas.mjs';
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const messages = read('src/app/chart/messages.json');
const images = read('shared/images/mapping.json');
const bundles = Object.fromEntries(['bb', 'dc', 'ngc'].map(version => [version, read(`src/app/generated/${version}.json`)]));
const make = (version = 'bb', params = {}) => {
  const bundle = bundles[version], state = readState(bundle, params);
  return buildChart(bundle, state, messages[version][state.lang], images);
};
const allRows = chart => chart.tables.flatMap(table => table.rows);
const allDrops = chart => allRows(chart).flatMap(row => row.cells.flatMap(cell => cell.drops));

test('every platform, language, difficulty and type preserves all row/cell/drop coordinates', () => {
  for (const [version, bundle] of Object.entries(bundles)) for (const lang of ['en', 'ja', 'zh']) {
    for (const [diff, types] of Object.entries(bundle.languages[lang].data)) for (const [type, episodes] of Object.entries(types)) {
      if (version !== 'bb' && type === 'boxes') {assert.deepEqual(episodes, {}); continue;}
      const chart = make(version, {lang, diff, type});
      assert.deepEqual(chart.tables.map(t => t.ep), Object.keys(episodes));
      const expected = Object.values(episodes).flat();
      assert.equal(chart.total, expected.length);
      assert.equal(chart.shown, expected.length);
      allRows(chart).forEach((row, i) => {
        assert.equal(row.cells.length, 10);
        row.cells.forEach((cell, j) => {
          const drops = cellDrops(expected[i].drops[j]).filter(d => d.item);
          assert.deepEqual(cell.drops.map(d => d.name), drops.map(d => d.item));
          assert.deepEqual(cell.drops.map(d => d.rare), drops.map(d => !!d.ss));
          assert.ok(cell.color && cell.text);
          for (const drop of cell.drops) assert.doesNotMatch(drop.rate, /NaN|Infinity/);
        });
      });
      assert.deepEqual(chart.sections.map(s => s.name), bundle.languages[lang].sectionIds);
      for (const section of chart.sections) assert.ok(fs.existsSync(`shared/images/section-ids/${section.icon}.png`));
    }
  }
});
test('DC converts conditional RDR to per-kill DR, including zero DAR and tiny rates', () => {
  for (const [diff, q, tooltip, rate] of [
    ['Normal', 'Dark Gunner', 'RDR = 0.22%', '0.0879%'],
    ['Ultimate', 'Dark Falz', 'RDR = 0.11%', '0%'],
    ['Normal', 'Al Rappy', 'RDR = 87.5%', '87.5%'],
    ['Ultimate', 'Sinow Blue', 'RDR = 0.000119%', '0.0000714%'],
  ]) assert.ok(allDrops(make('dc', {diff, q})).some(d => d.tooltip === tooltip && d.rate === rate));
  assert.equal(formatRate('0.009918212890625%', 'ngc', 'percent'), '0.00992%');
  assert.equal(formatRate('1.5625%', 'ngc', 'percent'), '1.56%');
});
test('BB forms, artwork and semantic Haven links preserve every identity and language', () => {
  const bundle = bundles.bb;
  for (const lang of ['en', 'ja', 'zh']) for (const diff of Object.keys(bundle.languages.en.data)) for (const type of ['monsters', 'boxes']) {
    const chart = make('bb', {lang, diff, type});
    for (const table of chart.tables) table.rows.forEach((row, index) => {
      const en = bundle.languages.en.data[diff][type][table.ep][index];
      const prefix = lang === 'zh' ? '' : '/' + lang;
      if (type === 'monsters') {
        const profile = bundle.monsters[table.ep][en.name], variant = profile[diff === 'Ultimate' ? 'ultimate' : 'normal'];
        assert.equal(row.name, variant.names[lang]);
        assert.equal(row.href, `https://www.psohaven.com${prefix}/enemies/${profile.id}/?diff=${{Normal:'n', Hard:'h', 'Very Hard':'vh', Ultimate:'u'}[diff]}`);
        assert.equal(row.image, variant.image ? '/bb/images/monsters/' + variant.image : null);
        if (row.image) assert.ok(fs.existsSync('.' + row.image));
      } else {
        assert.equal(row.href, null); assert.equal(row.image, null);
        assert.equal(row.name, bundle.languages[lang].data[diff].boxes[table.ep][index].name.replaceAll('/', '\n'));
      }
      row.cells.forEach((cell, column) => {
        const expected = cellDrops(en.drops[column]).filter(d => d.item);
        cell.drops.forEach((drop, i) => assert.equal(drop.href, `https://www.psohaven.com${prefix}/items/${bundle.items[expected[i].item]}/`));
      });
    });
  }
});
test('authority Chinese and episode-specific Japanese names remain intact', () => {
  const authority = read('i18n_names.json').monsters;
  for (const profiles of Object.values(bundles.bb.monsters)) for (const profile of Object.values(profiles)) {
    for (const variant of [profile.normal, profile.ultimate]) assert.equal(variant.names.zh, authority[variant.names.en].zh);
  }
  assert.equal(bundles.bb.monsters['Episode 1']['Gilchic/Gilchich'].ultimate.names.ja, 'ギルチッチ');
  assert.equal(bundles.bb.monsters['Episode 2']['Gilchic/Gilchich'].ultimate.names.ja, 'ギルチック');
});
test('search normalizes widths and matches alternate forms across language and difficulty', () => {
  assert.ok(fuzzyMatch('Ｈｅａｖｅｎ　Ｐｕｎｉｓｈｅｒ', 'heaven punisher'));
  assert.ok(fuzzyMatch('Heaven Punisher', 'ＨＰ'));
  assert.equal(allRows(make('bb', {q: '紫魔龟'}))[0].name, 'Booma');
  assert.equal(allRows(make('bb', {q: '紫魔龟', diff: 'Ultimate'}))[0].name, 'Bartle');
  assert.equal(allRows(make('bb', {q: '紫魔龟', diff: 'Ultimate', lang: 'ja'}))[0].name, 'バートル');
  assert.equal(make('bb', {q: '<script>not-a-monster</script>'}).shown, 0);
});
test('URL state round-trips and rejects unsupported/prototype-like values', () => {
  const valid = {lang:'zh', diff:'Ultimate', ep:'Episode 2', type:'boxes', rate:'fraction', q:'精灵'};
  const state = readState(bundles.bb, valid);
  assert.deepEqual(stateParams(state), valid);
  assert.deepEqual(make('bb', valid), make('bb', stateParams(state)));
  for (const version of ['bb','dc','ngc']) {
    for (const value of ['invalid','__proto__','constructor','toString']) {
      assert.deepEqual(make(version, {lang:value, diff:value, ep:value, type:value, rate:value}), make(version));
    }
    if (version !== 'bb') assert.deepEqual(make(version, {type:'boxes', rate:'fraction'}), make(version));
  }
});
test('every monster belongs to a contiguous area; BB areas match reviewed independent expectations', () => {
  for (const [version, bundle] of Object.entries(bundles)) for (const types of Object.values(bundle.languages.en.data)) {
    for (const [ep, rows] of Object.entries(types.monsters)) {
      let previous; const visited = new Set();
      for (const row of rows) {
        const area = areaFor(ep, row.name);
        assert.ok(area, `${version}/${ep}/${row.name}`);
        if (area !== previous) {assert.ok(!visited.has(area)); visited.add(area); previous = area;}
        if (version === 'bb') {
          const expected = Object.entries(reviewedAreas[ep]).find(([, names]) => names.split('|').includes(row.name.split('/')[0]))?.[0];
          assert.equal(area, expected);
        }
      }
    }
  }
  for (const lang of ['en','ja','zh']) for (const diff of Object.keys(bundles.bb.languages.en.data)) {
    for (const table of make('bb', {lang,diff}).tables) {
      let area;
      for (const row of table.rows) {
        area = row.heading || area;
        assert.equal(area, areaFor(table.ep, bundles.bb.languages.en.data[diff].monsters[table.ep][row.index].name));
      }
    }
  }
});
test('banner metadata yields correct colors and localized Hit hints without affecting boxes or legacy charts', () => {
  for (const lang of ['en', 'ja', 'zh']) {
    const drops = allDrops(make('bb', {lang, diff:'Ultimate'}));
    const source = Object.values(bundles.bb.languages[lang].data.Ultimate.monsters).flatMap(rows => rows.flatMap(row => row.drops.flatMap(cellDrops))).filter(d => d.item);
    assert.equal(drops.filter(d => d.hit).length, source.filter(d => d.bannerHit).length);
    assert.equal(drops.filter(d => d.rare).length, source.filter(d => d.ss).length);
    assert.ok(drops.filter(d => d.hit).every(d => d.hint.startsWith({en:'Banner requirement:', ja:'全体告知条件：', zh:'公告条件：'}[lang])));
    assert.ok(drops.some(d => d.href.includes('/frozen-shooter/') && d.hint.includes('≥ 30%')));
    assert.ok(drops.some(d => d.href.includes('/spread-needle/') && d.hint.includes('≥ 40%')));
    assert.ok(allDrops(make('bb', {lang, diff:'Ultimate',type:'boxes'})).every(d => !d.hit));
  }
  for (const version of ['dc','ngc']) {
    const drops = allDrops(make(version, {diff:'Ultimate'}));
    assert.ok(drops.some(d => d.rare));
    assert.ok(drops.every(d => !d.hit && !d.href));
  }
});
