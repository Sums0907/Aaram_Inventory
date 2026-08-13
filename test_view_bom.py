import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        page.on("console", lambda msg: print(f"PAGE LOG: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
        
        await page.goto("http://localhost:5173/inventory/boms")
        await page.wait_for_timeout(2000)
        
        print("Clicking View button on first BOM...")
        view_btns = await page.locator("button", has_text="View").all()
        if view_btns:
            await view_btns[0].click()
            await page.wait_for_timeout(2000)
            print("Clicked!")
        else:
            print("No view button found!")
            
        await browser.close()

asyncio.run(main())
