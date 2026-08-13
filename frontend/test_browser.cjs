const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  
  await page.goto('http://localhost:5173/inventory/boms');
  await page.waitForSelector('button');
  
  // click "New BOM"
  const buttons = await page.$$('button');
  for (const btn of buttons) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('New BOM')) {
      await btn.click();
      break;
    }
  }
  
  await page.waitForTimeout(1000);
  
  // click "Add Component"
  const allButtons = await page.$$('button');
  for (const btn of allButtons) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Add Component')) {
      await btn.click();
      break;
    }
  }
  
  await page.waitForTimeout(2000);
  await browser.close();
})();
