import {readFile, writeFile, mkdir} from 'node:fs/promises';
import vm from 'node:vm';

// Source JS is the data-pipeline interchange format. Never execute it in the browser.
await mkdir('src/app/generated', {recursive: true});
for (const version of ['bb', 'dc', 'ngc']) {
  const context = vm.createContext({window: {}});
  for (const language of ['en', 'ja', 'zh']) {
    vm.runInContext(await readFile(`${version}/data/${language}.js`, 'utf8'), context);
  }
  if (version === 'bb') vm.runInContext(await readFile('bb/data/monsters.js', 'utf8'), context);
  const bundle = {
    version,
    languages: Object.fromEntries(['en', 'ja', 'zh'].map(language => [language, context.window[`DROP_DATA_${language.toUpperCase()}`]])),
    monsters: context.window.BB_MONSTERS || {},
    items: context.window.BB_ITEMS || {},
  };
  await writeFile(`src/app/generated/${version}.json`, JSON.stringify(bundle));
}
