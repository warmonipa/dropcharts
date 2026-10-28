import {test, expect} from '@playwright/test';

const platforms = [
  {alias: 'bb', canonical: 'blue-burst', params: {lang: 'zh', diff: 'Ultimate', ep: 'Episode 4', type: 'boxes', rate: 'fraction', q: '光子'}},
  {alias: 'dc', canonical: 'dreamcast', params: {lang: 'zh', diff: 'Ultimate', q: '剑'}},
  {alias: 'ngc', canonical: 'gamecube', params: {lang: 'zh', diff: 'Ultimate', ep: 'Episode 2', q: '剑'}},
];

for (const {alias, canonical, params} of platforms) {
  test(`${alias}: all original HTTP paths preserve chart state at ${canonical}`, async ({page, request}) => {
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => {if (message.type() === 'error') errors.push(message.text());});
    const query = new URLSearchParams({...params, source: 'old-bookmark'}).toString();
    await page.goto(`/${canonical}/?${query}#content`);
    await expect(page.locator('#searchBox')).toHaveValue(params.q);
    const expected = await page.locator('#content').innerText();
    expect(await page.locator('td.monster-name').count()).toBeGreaterThan(0);

    for (const path of [`/${alias}`, `/${alias}/`, `/${alias}/index.html`]) {
      const response = await request.get(`${path}?${query}`, {maxRedirects: 0});
      if (path === `/${alias}`) {
        expect(response.status()).toBe(301);
        expect(response.headers().location).toBe(`/${alias}/?${query}`);
      } else {
        expect(response.status()).toBe(200);
        expect(await response.text()).toContain('class="drop-table"');
      }
      await page.goto(`${path}?${query}#content`);
      await expect(page.locator('#content')).toHaveText(expected, {useInnerText: true});
      await expect.poll(() => new URL(page.url()).pathname).toBe(`/${canonical}/`);
      const actual = new URL(page.url());
      for (const [key, value] of Object.entries(params)) expect(actual.searchParams.get(key)).toBe(value);
      expect(actual.searchParams.get('source')).toBe('old-bookmark');
      expect(actual.hash).toBe('#content');
    }
    expect(errors).toEqual([]);
  });
}

test('original home paths return HTTP 200 and retain bookmark context', async ({page, request}) => {
  for (const path of ['/', '/index.html']) {
    expect((await request.get(path)).status()).toBe(200);
    await page.goto(`${path}?source=old-bookmark#home`);
    await expect(page.locator('a.nav-card')).toHaveCount(3);
    await expect.poll(() => new URL(page.url()).pathname).toBe('/');
    expect(new URL(page.url()).searchParams.get('source')).toBe('old-bookmark');
    expect(new URL(page.url()).hash).toBe('#home');
  }
});
