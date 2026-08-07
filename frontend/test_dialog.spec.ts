import { test, expect } from '@playwright/test';

test('click manual adjustment', async ({ page }) => {
  await page.goto('http://localhost:5173/inventory/products');
  
  // Wait for products to load
  await page.waitForSelector('text=KD-RJ-RJP-KDB');
  
  // Click the product to open the dialog
  await page.click('text=KD-RJ-RJP-KDB');
  
  // Wait for the dialog to open
  await page.waitForSelector('text=Quick Actions');
  
  // Click Manual Adjustment button
  await page.click('text=Manual Adjustment');
  
  // See if Increase Stock dialog opens
  const isVisible = await page.isVisible('text=This will create a permanent manual adjustment');
  
  // Check for any console errors
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  
  console.log("Dialog visible?", isVisible);
});
