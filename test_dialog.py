import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:5173/inventory/products')
        
        # Wait for SKU to load
        await page.wait_for_selector('text=KD-RJ-RJP-KDB')
        
        # Click the SKU
        await page.click('text=KD-RJ-RJP-KDB')
        
        # Wait for dialog to open
        await page.wait_for_selector('text=Current Stock')
        
        # Check if the Manual Adjustment button exists and click it
        await page.click('text=Manual Adjustment')
        
        # Wait a bit
        await page.wait_for_timeout(1000)
        
        # Take a screenshot to see what is visible
        await page.screenshot(path='dialog_click.png')
        print("Screenshot saved to dialog_click.png")
        
        # Check if Increase Stock title is visible
        is_visible = await page.is_visible('text=This will create a permanent manual adjustment')
        print(f"Is Manual Adjustment dialog visible? {is_visible}")
        
        await browser.close()

asyncio.run(main())
