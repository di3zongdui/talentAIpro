const { chromium } = require('playwright');

(async () => {
  // Connect to running Chrome via CDP
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const defaultContext = browser.contexts()[0];
  const page = defaultContext.pages().find(p => p.url().includes('duolie.com'));

  if (!page) {
    console.log('No duolie page found. Opening...');
    const page = await defaultContext.newPage();
    await page.goto('https://www.duolie.com/newtalent/talentlist?menuCode=newtalent_allTalentMenu', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
  }

  console.log('Current URL:', page.url());

  // Try to find main search input
  // Option 1: Find by placeholder
  const searchInput = await page.locator('input[placeholder*="关键词"], input[placeholder*="人才"]').first();
  
  if (await searchInput.isVisible()) {
    console.log('Found search input');
    await searchInput.click();
    await page.waitForTimeout(500);
    
    // Clear existing
    await searchInput.fill('');
    await page.waitForTimeout(300);

    // Type the search description (simplified for search)
    const searchText = '车险高级精算专家 定价 费率 精算 北京 Python SAS GLM';
    await searchInput.fill(searchText);
    await page.waitForTimeout(500);
    
    console.log('Typed:', searchText);
    
    // Press Enter to search
    await searchInput.press('Enter');
    await page.waitForTimeout(3000);
    
    console.log('Search submitted');
  } else {
    console.log('Search input not found, trying alternative...');
    // Try all visible inputs
    const allInputs = await page.locator('input').all();
    for (const inp of allInputs) {
      const ph = await inp.getAttribute('placeholder');
      console.log('Input placeholder:', ph);
    }
  }

  // Take screenshot
  await page.screenshot({ path: 'C:\\Users\\George Guo\\WorkBuddy\\20260422151119\\duolie_search_result.png', fullPage: true });
  console.log('Screenshot saved');

  await browser.close();
})();
