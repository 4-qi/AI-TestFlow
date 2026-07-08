import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '..',
  timeout: 30000,
  use: {
    baseURL: 'http://127.0.0.1:5173',
  },
  webServer: [
    {
      command: 'conda run --no-capture-output -n AI-TestFlow python backend/app.py',
      cwd: '..',
      url: 'http://127.0.0.1:5000/api/health',
      reuseExistingServer: true,
      timeout: 30000,
    },
    {
      command: 'npm run dev -- --host 127.0.0.1',
      cwd: '.',
      url: 'http://127.0.0.1:5173',
      reuseExistingServer: true,
      timeout: 30000,
    },
  ],
});
