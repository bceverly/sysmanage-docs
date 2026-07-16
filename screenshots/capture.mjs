// Playwright capture driver for the SysManage documentation screenshots.
//
// Logs into a running instance, walks shotlist.json, and writes PNGs straight to
// ../assets/images/ (the exact paths the docs already <img>), so pass-one just
// refreshes the existing manually-made screenshots. Environment-agnostic: point it
// at the VM or any dev instance via SCREENSHOT_TARGET.
//
// Reuses the proven login flow from the repo's existing screenshot-generator.js
// (input[name="userid"] / input[name="password"] / button[type="submit"]).
//
//   SCREENSHOT_TARGET=http://localhost:3000 \
//   SCREENSHOT_USER=alice.admin@demo.sysmanage.org SCREENSHOT_PW=Demo-Pass-1! \
//   node capture.mjs
//
// Notes:
//  - SCREENSHOT_TARGET should point at the WEB UI (frontend) origin.
//  - Report shots drive the Reports page by visible name; if the UI labels differ,
//    tune `reportName` in shotlist.json (no code change needed).

import { chromium } from 'playwright';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dir = dirname(fileURLToPath(import.meta.url));
const TARGET = (process.env.SCREENSHOT_TARGET || 'http://localhost:3000').replace(/\/$/, '');
const USER = process.env.SCREENSHOT_USER || process.env.SCREENSHOT_ADMIN || 'admin@sysmanage.org';
const PW = process.env.SCREENSHOT_PW || process.env.SCREENSHOT_ADMIN_PW || '';
const OUT_DIR = join(__dir, '..', 'assets', 'images');
// Which tier to capture. OSS shots come from the unlicensed box, Pro shots from
// the Professional-licensed box — one shotlist, two runs, never mixed. A shot
// with no `tier` counts as oss (back-compat with the original OSS-only list).
const TIER = (process.env.SCREENSHOT_TIER || 'oss').toLowerCase();
// SCREENSHOT_ONLY=<name[,name...]> re-captures just those shots (handy for fixing
// a few failed shots, or the role-gated federation/air-gap pages that need a
// server-role flip + restart between passes). Matches by the shot's `name`,
// still within the selected tier.
const ONLY = (process.env.SCREENSHOT_ONLY || '').split(',').map(s => s.trim()).filter(Boolean);
const inTier = (s) =>
  (s.tier || 'oss').toLowerCase() === TIER && (ONLY.length === 0 || ONLY.includes(s.name));

const shotlist = JSON.parse(readFileSync(join(__dir, 'shotlist.json'), 'utf8'));

// Highlight freshly-added screenshots — a shot whose PNG did NOT exist before
// this run is printed in green with a `[new]` tag so new images (e.g. ones added
// for new docs) are easy to spot among the re-generated ones.
const GREEN = '\x1b[32m';
const RESET = '\x1b[0m';
let newCount = 0;
function logShot(shot, isNew, detail) {
  if (isNew) {
    newCount++;
    console.log(`  ${GREEN}✓ ${shot.out} [new]  (${detail})${RESET}`);
  } else {
    console.log(`  ✓ ${shot.out}  (${detail})`);
  }
}

// fqdn -> host id, written by seed.py, used to deep-link host-detail shots.
let hostIds = {};
try { hostIds = JSON.parse(readFileSync(join(__dir, 'host_ids.json'), 'utf8')); } catch { /* optional */ }

async function login(page) {
  await page.goto(`${TARGET}/login`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(1500);
  const userField = await page.$('input[name="userid"]');
  if (userField) {
    await page.fill('input[name="userid"]', USER);
    await page.fill('input[name="password"]', PW);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(5000); // let the SPA route to the dashboard
  } else {
    console.warn('  [login] no login form found — assuming already authenticated');
  }
  if (await page.$('input[name="password"]')) {
    throw new Error('login appears to have failed (still on login page) — check SCREENSHOT_USER/PW');
  }
}

// Settings and Host Detail switched from MUI <Tabs> to a left-rail of
// ListItemButtons (the nav redesign), so their sub-navigation is now
// role="button", not role="tab". Try the rail item first and fall back to a
// real MUI tab (Reports still uses tabs), so a shot's `tab` name works across
// both patterns. The rail is rendered before page content, so .first() lands on
// the nav item rather than a same-named button inside the panel.
async function selectTab(page, name) {
  const rail = page.getByRole('button', { name, exact: false });
  if (await rail.count()) {
    await rail.first().click({ timeout: 15000 });
    return;
  }
  await page.getByRole('tab', { name, exact: false }).first().click({ timeout: 15000 });
}

async function captureRoute(page, shot, vp) {
  await page.setViewportSize(shot.viewport || vp);
  await page.goto(`${TARGET}${shot.route}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(shotlist.settleMs || 2500);
  // Settings groups content into a left-rail (formerly MUI tabs); switch first.
  if (shot.tab) {
    await selectTab(page, shot.tab);
    await page.waitForTimeout(1200);
  }
  const out = join(OUT_DIR, shot.out);
  const isNew = !existsSync(out);
  await page.screenshot({ path: out, fullPage: false });
  logShot(shot, isNew, `${shot.route}${shot.tab ? ' #' + shot.tab : ''}`);
}

// Open a host detail view by deep-linking to /hosts/<id> (id resolved from the
// seed-written host_ids.json by the row's FQDN). The detail page reads its active
// tab from the URL hash, so `#<tabHash>` lands directly on a tab — far more robust
// than clicking a role-gated row icon or a scrollable MUI tab. Requires logging in
// as a user that can view host details (the admin has the VIEW_HOST_DETAILS role).
async function captureDetail(page, shot, vp) {
  await page.setViewportSize(shot.viewport || vp);
  const id = hostIds[shot.rowText];
  if (!id) throw new Error(`no host id for ${shot.rowText} (run seed first so host_ids.json exists)`);
  const url = `${TARGET}${shot.base || '/hosts'}/${id}${shot.tabHash ? '#' + shot.tabHash : ''}`;
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout((shotlist.settleMs || 2500) + 1500);
  // Plugin-injected host-detail tabs (Health, Vulnerabilities, ...) that aren't
  // addressable by URL hash are clicked by visible name — now left-rail buttons
  // after the nav redesign (selectTab falls back to a real tab if needed).
  if (shot.tab) {
    await selectTab(page, shot.tab);
    await page.waitForTimeout((shotlist.settleMs || 2500));
  }
  const out = join(OUT_DIR, shot.out);
  const isNew = !existsSync(out);
  await page.screenshot({ path: out, fullPage: false });
  logShot(shot, isNew, `detail: ${shot.rowText}${shot.tabHash ? ' #' + shot.tabHash : shot.tab ? ' tab:' + shot.tab : ''}`);
}

// Open a page, then optionally drive one interaction before shooting:
//  - shot.clickButton: click a button by visible name (opens a dialog, e.g.
//    "New Metric" / "Upload Key" → the define/upload dialog).
//  - shot.clickRowAction: click an action IconButton in the FIRST data row of a
//    MUI DataGrid, selected by 1-based index within that row's actions cell
//    (e.g. the "Graph" or "Assignments" icon → the metric graph / key
//    assignments sub-view). DataGrid action cells have no accessible name, so we
//    target them positionally via the standard [data-field="actions"] cell.
// Everything else mirrors captureRoute (viewport, goto, settle).
async function captureClick(page, shot, vp) {
  await page.setViewportSize(shot.viewport || vp);
  await page.goto(`${TARGET}${shot.route}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(shotlist.settleMs || 2500);
  let detail = shot.route;
  if (shot.clickButton) {
    await page.getByRole('button', { name: shot.clickButton, exact: false }).first().click({ timeout: 15000 });
    detail += ` » "${shot.clickButton}"`;
  }
  if (shot.clickRowAction) {
    const idx = shot.clickRowAction; // 1-based position within the actions cell
    const btn = page
      .locator('.MuiDataGrid-row [data-field="actions"] button')
      .nth(idx - 1);
    await btn.click({ timeout: 15000 });
    detail += ` » row action #${idx}`;
  }
  // Let the dialog animate in / the sub-view load its data (samples, assignments).
  await page.waitForTimeout(shot.clickSettleMs || (shotlist.settleMs || 2500) + 1500);
  const out = join(OUT_DIR, shot.out);
  const isNew = !existsSync(out);
  await page.screenshot({ path: out, fullPage: false });
  logShot(shot, isNew, detail);
}

async function captureReport(page, shot, vp) {
  await page.setViewportSize(shot.viewport || vp);
  await page.goto(`${TARGET}/reports`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(2000);
  // Reports are grouped into tabs (Hosts, Users, ...). Cards on a non-default tab
  // aren't in the DOM until that tab is selected, so switch first if specified.
  if (shot.tab) {
    await page.getByRole('tab', { name: shot.tab, exact: false }).first().click({ timeout: 15000 });
    await page.waitForTimeout(1000);
  }
  // Click the report card by its visible name, then the View action.
  const card = page.getByText(shot.reportName, { exact: false }).first();
  await card.click({ timeout: 15000 });
  await page.waitForTimeout(1000);
  // The viewer may expose a "View Report" button; click it if present.
  const viewBtn = page.getByRole('button', { name: /view report|view|preview/i }).first();
  if (await viewBtn.count()) {
    await viewBtn.click().catch(() => {});
  }
  await page.waitForTimeout(shotlist.settleMs || 3000);
  const out = join(OUT_DIR, shot.out);
  const isNew = !existsSync(out);
  await page.screenshot({ path: out, fullPage: false });
  logShot(shot, isNew, `report: ${shot.reportName}`);
}

async function main() {
  if (!PW) {
    console.error('ERROR: set SCREENSHOT_PW (a seeded user, e.g. from fixtures.json) or SCREENSHOT_ADMIN_PW.');
    process.exit(2);
  }
  const vp = { width: shotlist.viewportDefaults.width, height: shotlist.viewportDefaults.height };
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: vp,
    deviceScaleFactor: shotlist.viewportDefaults.deviceScaleFactor || 2,
    colorScheme: 'light',
  });
  const page = await context.newPage();

  console.log(`Capturing from ${TARGET} as ${USER} -> ${OUT_DIR}`);

  let ok = 0, fail = 0;
  // Pre-auth shots (e.g. the login page) — captured before we authenticate, on
  // the fresh unauthenticated page (after login the app redirects away from /login).
  for (const shot of shotlist.shots.filter((s) => s.type === 'login' && inTier(s))) {
    try {
      await page.setViewportSize(shot.viewport || vp);
      await page.goto(`${TARGET}${shot.route}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(shotlist.settleMs || 2500);
      const out = join(OUT_DIR, shot.out);
      const isNew = !existsSync(out);
      await page.screenshot({ path: out, fullPage: false });
      logShot(shot, isNew, `${shot.route}, pre-auth`);
      ok++;
    } catch (err) {
      console.error(`  ✗ ${shot.out}: ${err.message}`);
      fail++;
    }
  }

  await login(page);

  for (const shot of shotlist.shots) {
    // Skip non-shot entries: `_note` doc objects (no `out`) and skip/login types.
    if (!shot.out || shot.type === 'skip' || shot.type === 'login') continue;
    if (!inTier(shot)) continue;
    try {
      if (shot.type === 'report') await captureReport(page, shot, vp);
      else if (shot.type === 'detail') await captureDetail(page, shot, vp);
      else if (shot.type === 'click') await captureClick(page, shot, vp);
      else await captureRoute(page, shot, vp);
      ok++;
    } catch (err) {
      console.error(`  ✗ ${shot.out}: ${err.message}`);
      fail++;
    }
  }
  await browser.close();
  const total = shotlist.shots.filter(s => s.out && s.type !== 'skip' && inTier(s)).length;
  console.log(`\nCaptured ${ok}/${total} ${TIER} screenshots (${fail} failed).`);
  if (newCount) {
    console.log(`${GREEN}${newCount} new screenshot(s) generated this run (marked [new] above).${RESET}`);
  }
  process.exit(fail ? 1 : 0);
}

main();
