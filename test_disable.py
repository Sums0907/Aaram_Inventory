import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.goto("http://localhost:5173/inventory/products")
        await page.wait_for_timeout(2000)
        
        await page.click("tbody tr")
        await page.wait_for_timeout(1000)
        
        buttons = await page.query_selector_all("button")
        for btn in buttons:
            text = await btn.inner_text()
            if "Edit" in text:
                await btn.click()
                break
                
        await page.wait_for_timeout(1000)
        
        # Output all disabled elements
        disabled_elements = await page.query_selector_all("[disabled]")
        for el in disabled_elements:
            html = await el.evaluate("el => el.outerHTML")
            print(f"Disabled Element: {html}")
            
        await browser.close()

asyncio.run(main())
