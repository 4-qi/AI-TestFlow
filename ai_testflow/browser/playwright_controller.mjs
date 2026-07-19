import { createRequire } from 'node:module';
import fs from 'node:fs/promises';
import path from 'node:path';
import readline from 'node:readline';

const requireFromProject = createRequire(path.resolve(process.cwd(), 'package.json'));
const { chromium, firefox, webkit } = requireFromProject('@playwright/test');

let browser;
let context;
let page;
let baseUrl;
let timeoutMs;
let consoleErrors = [];
let failedRequests = [];

const input = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });

for await (const line of input) {
  if (!line.trim()) continue;
  try {
    const request = JSON.parse(line);
    const result = await handle(request);
    process.stdout.write(`${JSON.stringify({ ok: true, ...result })}\n`);
    if (request.command === 'close') break;
  } catch (error) {
    process.stdout.write(`${JSON.stringify({ ok: false, error: String(error?.stack || error) })}\n`);
  }
}

async function handle(request) {
  if (request.command === 'init') {
    const browserTypes = { chromium, firefox, webkit };
    const browserType = browserTypes[request.browser];
    if (!browserType) throw new Error(`Unsupported browser: ${request.browser}`);
    baseUrl = request.base_url;
    timeoutMs = request.timeout_ms;
    browser = await browserType.launch({ headless: request.headless });
    return {};
  }
  if (request.command === 'new_charter') {
    await closeContext();
    context = await browser.newContext();
    page = await context.newPage();
    page.setDefaultTimeout(timeoutMs);
    consoleErrors = [];
    failedRequests = [];
    page.on('console', message => {
      if (message.type() === 'error') consoleErrors.push(message.text());
    });
    page.on('pageerror', error => consoleErrors.push(String(error)));
    page.on('requestfailed', requestItem => {
      failedRequests.push({
        method: requestItem.method(),
        url: requestItem.url(),
        error: requestItem.failure()?.errorText || 'request failed',
      });
    });
    await page.goto(baseUrl);
    await settlePage();
    return {};
  }
  if (request.command === 'observe') {
    return { observation: await observe(request.screenshot_path) };
  }
  if (request.command === 'act') {
    await act(request.action);
    return {};
  }
  if (request.command === 'close') {
    await closeContext();
    if (browser) await browser.close();
    return {};
  }
  throw new Error(`Unsupported controller command: ${request.command}`);
}

async function observe(screenshotPath) {
  const body = page.locator('body');
  const visibleText = (await body.innerText()).slice(0, 12000);
  let accessibilitySnapshot = '';
  try {
    accessibilitySnapshot = (await body.ariaSnapshot()).slice(0, 16000);
  } catch (error) {
    accessibilitySnapshot = `ariaSnapshot unavailable: ${String(error)}`;
  }
  const interactiveElements = await page.locator('a,button,input,textarea,select,[role]').evaluateAll(elements =>
    elements.slice(0, 200).map((element, index) => ({
      index,
      tag: element.tagName.toLowerCase(),
      role: element.getAttribute('role') || '',
      name: element.getAttribute('aria-label') || element.innerText || '',
      label: element.labels?.[0]?.innerText || '',
      placeholder: element.getAttribute('placeholder') || '',
      type: element.getAttribute('type') || '',
      disabled: Boolean(element.disabled),
    }))
  );
  let savedScreenshotPath = null;
  if (screenshotPath) {
    await fs.mkdir(path.dirname(screenshotPath), { recursive: true });
    await page.screenshot({ path: screenshotPath, fullPage: true });
    savedScreenshotPath = screenshotPath;
  }
  return {
    current_url: page.url(),
    page_title: await page.title(),
    visible_text: visibleText,
    accessibility_snapshot: accessibilitySnapshot,
    interactive_elements: interactiveElements,
    console_errors: [...consoleErrors],
    failed_requests: [...failedRequests],
    screenshot_path: savedScreenshotPath,
  };
}

async function act(action) {
  if (action.action === 'navigate') {
    await page.goto(new URL(action.path, baseUrl).toString());
    await settlePage();
    return;
  }
  if (action.action === 'scroll') {
    await page.mouse.wheel(0, action.direction === 'down' ? 700 : -700);
    return;
  }
  if (action.action === 'wait') {
    await page.waitForTimeout(Math.min(action.milliseconds, 30000));
    return;
  }
  if (action.action === 'finish') return;
  const locator = await resolveTarget(action.target);
  if (action.action === 'fill') await locator.fill(action.value);
  else if (action.action === 'click') await locator.click();
  else if (action.action === 'press') await locator.press(action.key);
  else if (action.action === 'select_option') await locator.selectOption(action.option);
  else if (action.action === 'check') await locator.check();
  else throw new Error(`Unsupported browser action: ${action.action}`);
  await settlePage();
}

async function settlePage() {
  await page.waitForLoadState('domcontentloaded').catch(() => {});
  await page.waitForTimeout(300);
}

async function resolveTarget(target) {
  let locator;
  if (target.strategy === 'role') {
    locator = page.getByRole(target.role, { name: target.value, exact: true });
    if ((await locator.count()) === 0) locator = page.getByRole(target.role, { name: target.value });
  } else if (target.strategy === 'label') {
    locator = page.getByLabel(target.value, { exact: true });
    if ((await locator.count()) === 0) locator = page.getByLabel(target.value);
  } else if (target.strategy === 'text') {
    locator = page.getByText(target.value, { exact: true });
    if ((await locator.count()) === 0) locator = page.getByText(target.value);
  } else if (target.strategy === 'placeholder') {
    locator = page.getByPlaceholder(target.value, { exact: true });
    if ((await locator.count()) === 0) locator = page.getByPlaceholder(target.value);
  } else {
    throw new Error(`Unsupported target strategy: ${target.strategy}`);
  }
  const count = await locator.count();
  if (count === 0) throw new Error(`Target not found: ${JSON.stringify(target)}`);
  if (count > 1) throw new Error(`Target is ambiguous (${count} matches): ${JSON.stringify(target)}`);
  return locator;
}

async function closeContext() {
  if (context) await context.close();
  context = undefined;
  page = undefined;
}
