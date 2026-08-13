import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        page.on("console", lambda msg: print(f"PAGE LOG: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err.message}"))
        
        await page.goto("http://localhost:5173/inventory/boms")
        await page.wait_for_selector("button")
        
        # Click "New BOM"
        buttons = await page.query_selector_all("button")
        for btn in buttons:
            text = await btn.text_content()
            if text and "New BOM" in text:
                await btn.click()
                break
                
        await page.wait_for_timeout(1000)
        
        # Click "Add Component"
        buttons = await page.query_selector_all("button")
        for btn in buttons:
            text = await btn.text_content()
            if text and "Add Component" in text:
                await btn.click()
                break
                
        await page.wait_for_timeout(2000)
        await browser.close()

asyncio.run(main())
