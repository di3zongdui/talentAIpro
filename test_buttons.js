const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const results = [];

  const pages = [
    { name: '候选人端', file: 'frontend/candidate_dashboard.html' },
    { name: '顾问端', file: 'frontend/consultant_dashboard.html' },
    { name: '管理员端', file: 'frontend/admin_dashboard.html' }
  ];

  for (const p of pages) {
    console.log(`\n=== Testing ${p.name} ===`);
    const context = await browser.newContext();
    const page = await context.newPage();

    const filePath = path.join(process.cwd(), p.file);
    await page.goto(`file:///${filePath.replace(/\\/g, '/')}`);
    await page.waitForTimeout(500);

    const buttons = await page.$$('button');
    console.log(`Found ${buttons.length} buttons`);

    let clicked = 0;
    let failed = 0;
    const failedButtons = [];

    for (const btn of buttons) {
      const text = await btn.textContent();
      try {
        await btn.click({ timeout: 2000 });
        clicked++;
        console.log(`  OK: ${text.trim()}`);
      } catch (e) {
        failed++;
        failedButtons.push(text.trim());
        console.log(`  FAIL: ${text.trim()}`);
      }
    }

    results.push({ name: p.name, total: buttons.length, clicked, failed, failedButtons });
    await context.close();
  }

  await browser.close();

  console.log('\n=== Summary ===');
  let allOk = true;
  for (const r of results) {
    const status = r.failed === 0 ? 'ALL OK' : `${r.failed} FAILED`;
    console.log(`${r.name}: ${r.clicked}/${r.total} buttons clickable (${status})`);
    if (r.failed > 0) {
      console.log(`  Failed buttons: ${r.failedButtons.join(', ')}`);
      allOk = false;
    }
  }

  console.log(allOk ? '\n[SUCCESS] All buttons are clickable!' : '\n[WARNING] Some buttons failed');
  process.exit(allOk ? 0 : 1);
})();