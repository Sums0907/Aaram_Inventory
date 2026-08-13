import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("http://localhost:5173/inventory/products")
        await page.wait_for_timeout(2000)
        
        # Click first row
        print("Clicking first row...")
        await page.click("tbody tr")
        await page.wait_for_timeout(1000)
        
        # Click Edit button
        print("Clicking Edit button...")
        buttons = await page.query_selector_all("button")
        for btn in buttons:
            text = await btn.inner_text()
            if "Edit" in text:
                await btn.click()
                break
                
        await page.wait_for_timeout(1000)
        
        print("Checking Select triggers...")
        triggers = await page.query_selector_all("button[role='combobox']")
        for t in triggers:
            text = await t.text_content()
            html = await t.evaluate("el => el.outerHTML")
            print(f"Combobox: {html}")
            
        await browser.close()

asyncio.run(main())
