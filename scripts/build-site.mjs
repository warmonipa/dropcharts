import {execFileSync} from 'node:child_process';
import {cp, glob, mkdir, readFile, rename, rm, stat, writeFile} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {platforms} from '../src/app/platforms.ts';

execFileSync(process.execPath, ['scripts/generate-data.mjs'], {stdio: 'inherit'});
execFileSync(process.execPath, ['node_modules/@angular/cli/bin/ng.js', 'build'], {stdio: 'inherit', env: {...process.env, NG_BUILD_MAX_WORKERS: '2'}});
const output = 'dist/dropcharts/browser';
for (const route of ['', ...platforms.map(p => p.path + '/'), '404/']) {
  const html = await readFile(`${output}/${route}index.html`, 'utf8');
  if (!html.includes('ngh=') || !html.includes('ng-state')) throw new Error(`Missing hydration: ${route}`);
  if (route && route !== '404/' && !html.includes('class="drop-table"')) throw new Error(`Missing prerendered table: ${route}`);
  if (/window\.(?:DROP_DATA|initViewer)|__ASSET_VERSION__|\son(?:click|input)=/.test(html)) throw new Error(`Obsolete runtime: ${route}`);
}
await cp(`${output}/404/index.html`, `${output}/404.html`);
await rm(`${output}/404`, {recursive: true});
// Angular emits a CSR index for dynamic hosting; Pages must serve only prerendered entries.
await rm(`${output}/index.csr.html`, {force: true});
// Pages cannot issue configured HTTP redirects. Alias entry documents use the
// canonical prerendered tree; Angular redirects with query and fragment intact.
for (const {version: alias, path: canonical} of platforms) {
  await mkdir(`${output}/${alias}`, {recursive: true});
  await cp(`${output}/${canonical}/index.html`, `${output}/${alias}/index.html`);
}
const files = [];
for await (const file of glob('**/*', {cwd: output, exclude: ['**/.*']})) {
  if (!(await stat(`${output}/${file}`)).isFile()) continue;
  const bytes = await readFile(`${output}/${file}`);
  files.push({file, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')});
}
await writeFile(`${output}/build-manifest.json`, JSON.stringify({routes: ['/', ...platforms.map(p => `/${p.path}/`)], aliases: Object.fromEntries(platforms.map(p => [p.version, p.path])), files: files.sort((a,b) => a.file.localeCompare(b.file))}, null, 2));
const backup = '.site-build';
await rm(backup, {recursive: true, force: true});
if (existsSync('_site')) await rename('_site', backup);
try {await rename(output, '_site');} catch (error) {if (existsSync(backup)) await rename(backup, '_site'); throw error;}
await rm(backup, {recursive: true, force: true});
console.log('Built and verified Angular static site in _site');
