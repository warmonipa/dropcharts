import {createServer} from 'node:http';
import {readFile, stat} from 'node:fs/promises';
import path from 'node:path';
const root = path.resolve('_site');
const mime = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml'};
createServer(async (request, response) => {
  try {
    const url = new URL(request.url, 'http://localhost');
    let file = path.resolve(root, '.' + decodeURIComponent(url.pathname));
    if (!file.startsWith(root + path.sep) && file !== root) {response.writeHead(403).end(); return;}
    if ((await stat(file)).isDirectory()) {
      if (!url.pathname.endsWith('/')) {response.writeHead(301, {location: url.pathname + '/' + url.search}).end(); return;}
      file = path.join(file, 'index.html');
    }
    response.writeHead(200, {'Content-Type': mime[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store'});
    response.end(await readFile(file));
  } catch {
    response.writeHead(404, {'Content-Type': 'text/html; charset=utf-8'});
    response.end(await readFile(path.join(root, '404.html')));
  }
}).listen(Number(process.env.PORT || 4173), '127.0.0.1', () => console.log('Preview: http://127.0.0.1:' + (process.env.PORT || 4173)));
