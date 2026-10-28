import {defineConfig} from '@playwright/test';
export default defineConfig({
  testDir: './tests/e2e', timeout: 45000, workers: 2,
  use: {baseURL: 'http://127.0.0.1:4173', trace: 'retain-on-failure'},
  webServer: {command: 'node scripts/serve-site.mjs', url: 'http://127.0.0.1:4173', reuseExistingServer: false},
});
