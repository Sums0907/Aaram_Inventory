import * as puppeteer from 'puppeteer';

async function runSmokeTest() {
  console.log("Starting smoke test...");
  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();
  
  try {
    const baseUrl = 'http://localhost:5173';
    
    // 1. Dashboard
    console.log("Navigating to Job Worker Accounting Dashboard...");
    const dashboardResponse = await page.goto(`${baseUrl}/accounting/job-worker/dashboard`);
    if (!dashboardResponse?.ok()) throw new Error(`Dashboard failed to load: ${dashboardResponse?.status()}`);
    console.log("Dashboard loaded successfully.");
    
    // 2. Payables Workspace
    console.log("Navigating to Job Worker Payables Workspace...");
    const payablesResponse = await page.goto(`${baseUrl}/accounting/job-worker/payables`);
    if (!payablesResponse?.ok()) throw new Error(`Payables failed to load: ${payablesResponse?.status()}`);
    console.log("Payables Workspace loaded successfully.");
    
    // 3. Rates Page
    console.log("Navigating to Job Work Rates...");
    const ratesResponse = await page.goto(`${baseUrl}/accounting/job-worker/rates`);
    if (!ratesResponse?.ok()) throw new Error(`Rates failed to load: ${ratesResponse?.status()}`);
    console.log("Rates loaded successfully.");
    
    console.log("Smoke test passed!");
  } catch (error) {
    console.error("Smoke test failed:", error);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runSmokeTest();
