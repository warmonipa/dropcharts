const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
function viewer(version = 'bb', query = '') {
  const nodes = new Map();
  const element = () => ({innerHTML: '', value: '', children: [], style: {setProperty() {}}, dataset: {}, appendChild(child) {this.children.push(child);}});
  const document = {documentElement: {}, body: element(), addEventListener() {}, createElement: element,
    getElementById(id) {if (!nodes.has(id)) nodes.set(id, element()); return nodes.get(id);}, querySelectorAll() {return [];}};
  const window = {location: new URL('https://dropcharts.psohaven.com/'+version+'/'+query), addEventListener() {}};
  window.history = {replaceState(_state, _title, url) {window.location = new URL(url);}};
  const context = vm.createContext({window, document, URL, URLSearchParams, XMLHttpRequest: class {open() {} send() {}}});
  for (const file of [`${version}/data/en.js`, `${version}/data/ja.js`, `${version}/data/zh.js`, 'bb/data/monsters.js', 'shared/i18n.js', 'shared/viewer.js']) {
    vm.runInContext(fs.readFileSync(path.join(root, file), 'utf8'), context);
  }
  window.initViewer({version, languages: ['en','ja','zh'], episodes: version === 'dc' ? null : version === 'bb' ? ['Episode 1','Episode 2','Episode 4'] : ['Episode 1','Episode 2'], hasTypes: version === 'bb', hasRateToggle: version === 'bb'});
  return {window, document, nodes, html: () => document.getElementById('content').innerHTML};
}
test('every BB row uses the selected form and locally available artwork in all languages and difficulties', () => {
  for (const lang of ['en','ja','zh']) for (const diff of ['Normal','Hard','Very Hard','Ultimate']) {
    const app = viewer('bb', `?lang=${lang}&diff=${diff}`);
    const names = [...app.html().matchAll(/class="mob-name">([^<]*)</g)].map(match => match[1]);
    const expected = [];
    for (const [episode, rows] of Object.entries(app.window.DROP_DATA_EN.data[diff].monsters)) for (const row of rows) {
      const profile = app.window.BB_MONSTERS[episode][row.name];
      const variant = profile[diff === 'Ultimate' ? 'ultimate' : 'normal'];
      expected.push(variant.names[lang]);
      if (variant.image) {
        assert.ok(fs.existsSync(path.join(root, 'bb/images/monsters', variant.image)));
        assert.ok(variant.source.startsWith('https://wiki.pioneer2.net/'));
      }
    }
    assert.deepEqual(names, expected);
    const previews = [...app.html().matchAll(/class="monster-tooltip-img" src="images\/monsters\/([^"<>]+)"/g)].map(match => match[1]);
    const expectedPreviews = Object.entries(app.window.DROP_DATA_EN.data[diff].monsters).flatMap(([episode, rows]) =>
      rows.map(row => app.window.BB_MONSTERS[episode][row.name][diff === 'Ultimate' ? 'ultimate' : 'normal'].image).filter(Boolean));
    assert.deepEqual(previews, expectedPreviews);
    assert.doesNotMatch(app.html(), /class="monster-icon/);
    assert.equal(app.document.documentElement.lang, lang);
  }
});
test('table context is restored after reload or returning from a detail page', () => {
  const app = viewer();
  app.nodes.get('difficultyBtns').children.find(button => button.dataset.diff === 'Ultimate').onclick();
  app.nodes.get('langBtns').children.find(button => button.dataset.lang === 'zh').onclick();
  app.window._viewer.setEpisode('Episode 2');
  app.window._viewer.setRateFormat('fraction');
  app.document.getElementById('searchBox').value = 'Gilchich';
  app.window.onSearch();
  const params = app.window.location.searchParams;
  assert.equal(params.get('diff'), 'Ultimate');
  assert.equal(params.get('lang'), 'zh');
  assert.equal(params.get('ep'), 'Episode 2');
  assert.equal(params.get('rate'), 'fraction');
  assert.equal(params.get('q'), 'Gilchich');
  const restored = viewer('bb', app.window.location.search);
  assert.equal(restored.html(), app.html());
  assert.equal(restored.document.getElementById('searchBox').value, 'Gilchich');
  app.document.getElementById('searchBox').value = '';
  app.window.onSearch();
  app.window._viewer.setType('boxes');
  assert.equal(app.window.location.searchParams.get('type'), 'boxes');
  assert.equal(viewer('bb', app.window.location.search).html(), app.html());
});
test('unsupported URL context cannot hide tables or apply BB-only controls to legacy versions', () => {
  for (const version of ['bb','dc','ngc']) {
    for (const invalid of ['invalid', '__proto__', 'constructor', 'toString']) {
      const app = viewer(version, `?diff=${invalid}&lang=${invalid}&ep=${invalid}&type=${invalid}&rate=${invalid}`);
      assert.equal(app.html(), viewer(version).html());
    }
    if (version !== 'bb') {
      const legacy = viewer(version, '?type=boxes&rate=fraction');
      assert.equal(legacy.html(), viewer(version).html());
      assert.equal(legacy.window.location.search, '');
    }
  }
});
test('generated Chinese names match authority and Wiki episode-specific Japanese labels remain explicit', () => {
  const app = viewer();
  const authority = JSON.parse(fs.readFileSync(path.join(root, 'i18n_names.json'), 'utf8')).monsters;
  for (const profiles of Object.values(app.window.BB_MONSTERS)) for (const profile of Object.values(profiles)) {
    for (const variant of [profile.normal, profile.ultimate]) {
      assert.equal(variant.names.zh, authority[variant.names.en].zh);
    }
  }
  // Ephinea Wiki /w/Gillchic, checked 2026-09-18: the source itself has
  // different Japanese Ultimate labels in EP1 and EP2. Do not flatten them.
  assert.equal(app.window.BB_MONSTERS['Episode 1']['Gilchic/Gilchich'].ultimate.names.ja, 'ギルチッチ');
  assert.equal(app.window.BB_MONSTERS['Episode 2']['Gilchic/Gilchich'].ultimate.names.ja, 'ギルチック');
});
test('alternate form and language searches survive difficulty changes', () => {
  const app = viewer();
  app.document.getElementById('searchBox').value = '紫魔龟';
  app.window.onSearch();
  assert.match(app.html(), /class="mob-name">Booma</);
  app.nodes.get('difficultyBtns').children.find(button => button.dataset.diff === 'Ultimate').onclick();
  assert.match(app.html(), /class="mob-name">Bartle</);
  assert.doesNotMatch(app.html(), /class="mob-name">Booma</);
  app.nodes.get('langBtns').children.find(button => button.dataset.lang === 'ja').onclick();
  assert.match(app.html(), /class="mob-name">バートル</);
});
test('box rows retain their location names and have no monster portraits', () => {
  const app = viewer();
  app.window._viewer.setType('boxes');
  assert.doesNotMatch(app.html(), /class="monster-tooltip-img/);
  for (const rows of Object.values(app.window.DROP_DATA_EN.data.Normal.boxes)) for (const row of rows) {
    assert.ok(app.html().includes(row.name.replaceAll('/', '<br>')));
  }
});
test('DC and GameCube render without the BB identity map', () => {
  for (const version of ['dc', 'ngc']) {
    const app = viewer(version, '?diff=Ultimate');
    delete app.window.BB_MONSTERS;
    app.window.onSearch();
    assert.match(app.html(), /class="mob-name"/);
    assert.doesNotMatch(app.html(), /class="monster-tooltip-img/);
  }
});
test('every BB monster and item links to its Wiki identity with the selected context', () => {
  for (const lang of ['en', 'ja', 'zh']) for (const diff of ['Normal', 'Hard', 'Very Hard', 'Ultimate']) {
    const app = viewer('bb', `?lang=${lang}&diff=${diff}`);
    for (const kind of ['monsters', 'boxes']) {
      app.window._viewer.setType(kind);
      const monsterLinks = [...app.html().matchAll(/class="monster-link monster-label" href="([^"]+)"/g)].map(m => m[1]);
      const itemLinks = [...app.html().matchAll(/class="item-name[^"]*" href="([^"]+)"/g)].map(m => m[1]);
      const expectedMonsters = [], expectedItems = [];
      for (const [episode, rows] of Object.entries(app.window.DROP_DATA_EN.data[diff][kind])) for (const row of rows) {
        if (kind === 'monsters') {
          const profile = app.window.BB_MONSTERS[episode][row.name];
          const code = {Normal:'n', Hard:'h', 'Very Hard':'vh', Ultimate:'u'}[diff];
          expectedMonsters.push(`https://www.psohaven.com/data/enemies/${profile.id}.html?diff=${code}&amp;lang=${lang}`);
        }
        for (const cell of row.drops) for (const drop of cell.items || [cell]) {
          if (drop.item) {
            assert.ok(app.window.BB_ITEMS[drop.item], drop.item);
            expectedItems.push(`https://www.psohaven.com/data/items/${app.window.BB_ITEMS[drop.item]}.html?lang=${lang}`);
          }
        }
      }
      assert.deepEqual(monsterLinks, expectedMonsters);
      assert.deepEqual(itemLinks, expectedItems);
    }
  }
});
