const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const vm = require('node:vm');
const {spawnSync} = require('node:child_process');

function fixture(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'drop-wiki-sync-'));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  const root = path.join(dir, 'drop'), wiki = path.join(dir, 'wiki');
  const write = (file, value) => {
    fs.mkdirSync(path.dirname(file), {recursive:true});
    fs.writeFileSync(file, typeof value === 'string' ? value : JSON.stringify(value));
  };
  write(root+'/tools/sync_wiki_catalog.cjs', fs.readFileSync(path.join(__dirname, '../tools/sync_wiki_catalog.cjs'), 'utf8'));
  write(root+'/i18n_names.json', {monsters:{Booma:{ja:'ブーマ',zh:'棕狂熊'},Bartle:{ja:'バートル',zh:'紫魔龟'}}});
  write(root+'/bb/data/en.js', 'window.DROP_DATA_EN = '+JSON.stringify({data:{Normal:{monsters:{'Episode 1':[{name:'Booma/Bartle',drops:[{items:[{item:'Saber',rate:'1/2'},{item:'Brand',rate:'1/3'}]}]}]}}}})+';');
  const monster = {id:'booma',episode:1,names:{en:'Booma',ja:'ブーマ'},ultimateNames:{en:'Bartle',ja:'バートル'},image:'/assets/normal.png',ultimateImage:'/assets/ultimate.png'};
  write(wiki+'/src/app/generated/monster-catalog/index.json', [monster]);
  write(wiki+'/src/app/generated/monster-catalog/details.server.json', {booma:{drops:{n:{name:'Booma/Bartle'}}}});
  write(wiki+'/src/app/generated/item-catalog/index.json', [['saber','Saber'],['brand','Brand']]);
  write(wiki+'/content/monster-catalog/images.json', {Booma:{path:'/assets/normal.png',page:'https://wiki.pioneer2.net/w/File:Booma.png'},Bartle:{path:'/assets/ultimate.png',page:'https://wiki.pioneer2.net/w/File:Bartle.png'}});
  write(wiki+'/assets/normal.png', 'normal image');
  write(wiki+'/assets/ultimate.png', 'ultimate image');
  write(root+'/bb/images/monsters/old.png', 'old image');
  write(root+'/bb/data/monsters.js', 'old manifest');
  const run = () => spawnSync(process.execPath, [root+'/tools/sync_wiki_catalog.cjs', wiki], {encoding:'utf8'});
  return {root,wiki,write,run};
}

test('a rejected item mapping leaves the published manifest and artwork untouched', t => {
  const f = fixture(t);
  f.write(f.wiki+'/src/app/generated/item-catalog/index.json', [['saber','Saber']]);
  const result = f.run();
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /Missing item detail: Brand/);
  assert.equal(fs.readFileSync(f.root+'/bb/data/monsters.js','utf8'), 'old manifest');
  assert.deepEqual(fs.readdirSync(f.root+'/bb/images/monsters'), ['old.png']);
  assert.equal(fs.readFileSync(f.root+'/bb/images/monsters/old.png','utf8'), 'old image');
});

test('missing artwork is validated before any generated file changes', t => {
  const f = fixture(t);
  fs.unlinkSync(f.wiki+'/assets/ultimate.png');
  assert.notEqual(f.run().status, 0);
  assert.equal(fs.readFileSync(f.root+'/bb/data/monsters.js','utf8'), 'old manifest');
  assert.deepEqual(fs.readdirSync(f.root+'/bb/images/monsters'), ['old.png']);
});

test('successful sync updates both forms, nested item identities, and retires unused artwork', t => {
  const f = fixture(t);
  const result = f.run();
  assert.equal(result.status, 0, result.stderr);
  const context = {window:{}};
  vm.runInNewContext(fs.readFileSync(f.root+'/bb/data/monsters.js','utf8'), context);
  const profile = context.window.BB_MONSTERS['Episode 1']['Booma/Bartle'];
  assert.equal(profile.normal.names.zh, '棕狂熊');
  assert.equal(profile.ultimate.names.ja, 'バートル');
  assert.equal(context.window.BB_ITEMS.Brand, 'brand');
  assert.deepEqual(fs.readdirSync(f.root+'/bb/images/monsters').sort(), ['normal.png','ultimate.png']);
  assert.equal(fs.readFileSync(f.root+'/bb/images/monsters/ultimate.png','utf8'), 'ultimate image');
  const manifest = fs.readFileSync(f.root+'/bb/data/monsters.js','utf8');
  assert.equal(f.run().status, 0);
  assert.equal(fs.readFileSync(f.root+'/bb/data/monsters.js','utf8'), manifest);
});
