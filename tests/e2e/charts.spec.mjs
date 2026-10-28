import {test, expect} from '@playwright/test';

test.beforeEach(async ({page}) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => {if (message.type() === 'error') errors.push(message.text());});
  page.errors = errors;
});
test.afterEach(async ({page}) => {expect(page.errors).toEqual([]);});

test('all entry points have actual prerendered content without JavaScript', async ({browser, request}) => {
  const context = await browser.newContext({javaScriptEnabled: false});
  const page = await context.newPage();
  for (const version of ['blue-burst', 'dreamcast', 'gamecube', 'bb', 'dc', 'ngc']) {
    await page.goto('/' + version + '/');
    await expect(page.locator('.drop-table').first()).toBeVisible();
    expect(await page.locator('td.monster-name').count()).toBeGreaterThan(30);
    await expect(page.locator('thead').first().locator('th')).toHaveCount(11);
  }
  const response = await request.get('/dc?lang=zh', {maxRedirects: 0});
  expect(response.status()).toBe(301);
  expect(response.headers().location).toBe('/dc/?lang=zh');
  const missing = await request.get('/missing-page/');
  expect(missing.status()).toBe(404);
  expect(await missing.text()).toContain('Page not found');
  await context.close();
});
test('Angular navigation mounts each platform without stale controls or global viewer', async ({page}) => {
  await page.goto('/');
  await page.locator('a.nav-card').filter({hasText:'PSOBB'}).click();
  await expect(page).toHaveURL(/\/blue-burst\/$/);
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', 'https://dropcharts.psohaven.com/blue-burst/');
  await expect(page.locator('#typeBtns')).toBeVisible();
  await page.locator('.platform-nav a').filter({hasText:/^DC$/}).click();
  await expect(page.locator('#pageTitle')).toContainText('PSO DC');
  await expect(page.locator('#typeBtns')).toHaveCount(0);
  await expect(page.locator('#episodeBtns')).toHaveCount(0);
  await page.locator('.platform-nav a').filter({hasText:/^NGC$/}).click();
  await expect(page.locator('#episodeBtns')).toBeVisible();
  await expect(page.locator('#rateBtns')).toHaveCount(0);
  expect(await page.evaluate(() => ['initViewer','_viewer','DROP_DATA_EN','I18N'].filter(key => key in window))).toEqual([]);
});
test('query deep link hydrates boxes, all drops, language and selected rate without mismatch', async ({page}) => {
  await page.goto('/bb/?lang=zh&diff=Ultimate&type=boxes&ep=Episode%204&rate=fraction');
  await expect(page.locator('html')).toHaveAttribute('lang','zh');
  await expect(page.locator('[data-type="boxes"]')).toHaveAttribute('aria-pressed','true');
  await expect(page.locator('.episode-section')).toHaveCount(1);
  await expect(page.locator('.monster-link')).toHaveCount(0);
  const multi = page.locator('td.drop-cell').filter({has: page.locator('.drop-option:nth-child(2)')});
  expect(await multi.count()).toBeGreaterThan(0);
  await expect(multi.first().locator('.drop-rate').first()).toContainText('/');
  const before = await page.locator('#content').innerText();
  await page.reload();
  await expect(page.locator('#content')).toHaveText(before, {useInnerText: true});
});
test('filters, alternate-language search, reload and history restore URL context', async ({page}) => {
  await page.goto('/bb/');
  await page.locator('#searchBox').fill('紫魔龟');
  await expect(page.locator('.mob-name')).toHaveText('Booma');
  await page.locator('[data-diff="Ultimate"]').click();
  await expect(page.locator('.mob-name')).toHaveText('Bartle');
  await page.locator('[data-lang="ja"]').click();
  await expect(page.locator('.mob-name')).toHaveText('バートル');
  await expect(page.locator('.monster-link')).toHaveAttribute('href', /\/ja\/enemies\/.*\?diff=u$/);
  await page.reload();
  await expect(page.locator('.mob-name')).toHaveText('バートル');
  await page.locator('.platform-nav a').filter({hasText:/^DC$/}).click();
  await expect(page.locator('#typeBtns')).toHaveCount(0);
  await page.goBack();
  await expect(page.locator('.mob-name')).toHaveText('バートル');
});
test('invalid URL values normalize without hiding tables', async ({page}) => {
  await page.goto('/ngc/?lang=constructor&diff=__proto__&type=boxes&rate=fraction&ep=missing');
  await expect(page.locator('.drop-table').first()).toBeVisible();
  await expect(page).toHaveURL(/\/gamecube\/$/);
});
test('original index.html HTTP entries retain query state after Angular takes over', async ({page, request}) => {
  for (const [version, canonical] of [['bb','blue-burst'], ['dc','dreamcast'], ['ngc','gamecube']]) {
    const url = `/${version}/index.html?lang=ja&diff=Ultimate&q=test-no-results&source=bookmark#content`;
    const response = await request.get(url);
    expect(response.status()).toBe(200);
    expect(await response.text()).toContain('class="drop-table"');
    await page.goto(url);
    await expect(page.locator('html')).toHaveAttribute('lang', 'ja');
    await expect(page.locator('[data-diff="Ultimate"]')).toHaveAttribute('aria-pressed', 'true');
    await expect(page.locator('#searchBox')).toHaveValue('test-no-results');
    await expect(page.locator('.no-results')).toBeVisible();
    expect(new URL(page.url()).searchParams.get('diff')).toBe('Ultimate');
    expect(new URL(page.url()).searchParams.get('source')).toBe('bookmark');
    expect(new URL(page.url()).pathname).toBe(`/${canonical}/`);
    expect(new URL(page.url()).hash).toBe('#content');
    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', `https://dropcharts.psohaven.com/${canonical}/`);
  }
  await page.goto('/index.html');
  await expect(page.locator('a.nav-card')).toHaveCount(3);
});
test('portrait and rate previews respond to focus, Escape, scroll and navigation', async ({page}) => {
  await page.goto('/bb/');
  const link = page.locator('.monster-link[data-preview]').first();
  await link.focus();
  await expect(page.locator('#item-tooltip')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.locator('#item-tooltip')).toHaveCount(0);
  const rate = page.locator('.has-rdr').first();
  await rate.focus();
  await expect(page.locator('#rate-tooltip')).toBeVisible();
  await page.locator('.table-wrap').first().evaluate(el => {el.scrollLeft = 200;});
  await expect(page.locator('#rate-tooltip')).toHaveCount(0);
  await page.locator('.platform-nav a').filter({hasText:/^DC$/}).click();
  await expect(page.locator('#item-tooltip')).toHaveCount(0);
});
test('mobile table retains frozen identity and centered area label after horizontal scroll', async ({page}) => {
  await page.setViewportSize({width:390, height:844});
  await page.goto('/bb/');
  const wrap = page.locator('.table-wrap').first();
  await expect(wrap).toHaveCSS('--area-label-center', /px$/);
  const label = wrap.locator('.area-label').first(), monster = wrap.locator('td.monster-name').first();
  const before = {label: await label.boundingBox(), monster: await monster.boundingBox()};
  await wrap.evaluate(el => {el.scrollLeft = 600;});
  // Collapsed table borders move the sticky edge by half a CSS pixel.
  await expect.poll(async () => Math.abs((await monster.boundingBox()).x - before.monster.x)).toBeLessThanOrEqual(1);
  expect(Math.abs((await label.boundingBox()).x - before.label.x)).toBeLessThanOrEqual(1);
  const box = await wrap.boundingBox(), heading = await label.boundingBox();
  expect(Math.abs(heading.x + heading.width / 2 - box.x - box.width / 2)).toBeLessThanOrEqual(1);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await expect(page.locator('.sticky-toolbar')).toHaveCSS('position','static');
  await page.screenshot({path:'test-results/mobile-chart.png', fullPage:true});
});
