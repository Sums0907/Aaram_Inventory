import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        page.on("console", lambda msg: print(f"PAGE LOG: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err.message}"))
        
        await page.goto("http://localhost:5173/inventory/products")
        await page.wait_for_timeout(2000)
        
        # Find Edit button and click it
        buttons = await page.query_selector_all("button")
        for btn in buttons:
            text = await btn.inner_text()
            if "Edit" in text or "edit" in text:
                print("Clicking Edit button...")
                await btn.click()
                break
                
        await page.wait_for_timeout(2000)
        
        print("Looking for Select triggers...")
        triggers = await page.query_selector_all("button[role='combobox']")
        for t in triggers:
            text = await t.text_content()
            disabled = await t.get_attribute("disabled")
            print(f"Combobox '{text}': disabled={disabled}")
        
        await browser.close()

asyncio.run(main())
