import {DefaultUrlSerializer, UrlTree} from '@angular/router';

/** Match GitHub Pages directory URLs for initial requests and client navigation. */
export class PublicUrlSerializer extends DefaultUrlSerializer {
  override parse(url: string): UrlTree {
    const [, path, suffix] = /^([^?#]*)(.*)$/.exec(url)!;
    return super.parse((path.replace(/\/+$/, '') || '/') + suffix);
  }
  override serialize(tree: UrlTree): string {
    const url = super.serialize(tree);
    const [, path, suffix] = /^([^?#]*)(.*)$/.exec(url)!;
    return path.endsWith('/') || /\.[a-z0-9]+$/i.test(path) ? url : path + '/' + suffix;
  }
}
