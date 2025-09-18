#!/usr/bin/env node

const { chromium } = require('playwright');
const path = require('path');

async function generateDashboardScreenshot() {
    console.log('🚀 Starting Playwright browser...');

    // Launch browser
    const browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-dev-shm-usage']
    });

    const page = await browser.newPage();

    // Set viewport size for consistent screenshot
    await page.setViewportSize({ width: 1400, height: 900 });

    console.log('📱 Navigating to SysManage dashboard...');

    try {
        // First, try to inject a mock authentication token to bypass login
        console.log('🔓 Attempting to bypass login with mock authentication...');

        // Navigate to the mockup dashboard HTML file
        const mockupPath = 'file://' + path.join(__dirname, 'mockup-dashboard.html');
        console.log(`📁 Loading mockup from: ${mockupPath}`);

        await page.goto(mockupPath, {
            waitUntil: 'networkidle',
            timeout: 30000
        });

        console.log('⏳ Waiting for mockup page to load...');

        // Wait for the mockup HTML to load - look for the main content
        await page.waitForFunction(() => {
            const mainContent = document.querySelector('.main-content');
            return mainContent && mainContent.children.length > 0;
        }, { timeout: 15000 });

        console.log('✅ Mockup page loaded!');

        // Wait a bit more for components to render
        await page.waitForTimeout(2000);

        // Check if we're on login page or dashboard by looking for common React elements
        const pageContent = await page.content();
        console.log('🔍 Page length:', pageContent.length);

        // Try to find login form elements
        const isLoginPage = await page.$('input[type="email"], input[type="password"], form');
        const hasLoginButton = await page.$('button[type="submit"]');

        if (isLoginPage || hasLoginButton) {
            console.log('🔐 Found login page, attempting to log in...');

            try {
                // Debug: list all input fields
                const allInputs = await page.$$eval('input', inputs =>
                    inputs.map(input => ({
                        type: input.type,
                        name: input.name,
                        placeholder: input.placeholder,
                        id: input.id,
                        className: input.className
                    }))
                );
                console.log('🔍 Found input fields:', JSON.stringify(allInputs, null, 2));

                // Try multiple credential combinations
                const credentials = [
                    { userid: 'admin', password: 'admin' },
                    { userid: 'admin@sysmanage.local', password: 'admin' },
                    { userid: 'demo', password: 'demo' },
                    { userid: 'test', password: 'test' },
                    { userid: 'admin', password: 'password' }
                ];

                let loginSuccess = false;
                for (const cred of credentials) {
                    console.log(`🔐 Trying credentials: ${cred.userid} / ${cred.password}`);

                    // Fill the userid field (found via debug)
                    const useridField = await page.$('input[name="userid"]');
                    if (useridField) {
                        await useridField.selectAll();
                        await useridField.fill(cred.userid);
                        console.log('📧 Filled userid field');
                    }

                    // Fill the password field (found via debug)
                    const passwordField = await page.$('input[name="password"]');
                    if (passwordField) {
                        await passwordField.selectAll();
                        await passwordField.fill(cred.password);
                        console.log('🔑 Filled password field');
                    }

                    // Click login button
                    const loginButton = await page.$('button[type="submit"], .login-button, .btn-primary, button:has-text("Login"), button:has-text("Sign in"), button:has-text("Enter")');
                    if (loginButton) {
                        await loginButton.click();
                        console.log('🖱️ Clicked login button');
                    }

                    // Wait and check if login succeeded
                    await page.waitForTimeout(3000);
                    const stillOnLoginPage = await page.$('input[type="password"]');
                    if (!stillOnLoginPage) {
                        console.log('✅ Login successful!');
                        loginSuccess = true;
                        break;
                    } else {
                        console.log('❌ Login failed, trying next credentials...');
                    }
                }

                if (!loginSuccess) {
                    console.log('⚠️ All login attempts failed');
                }

                // Wait for dashboard elements to appear (not login elements)
                try {
                    await page.waitForFunction(() => {
                        // Wait until we're no longer on login page
                        const loginForm = document.querySelector('input[type="password"]');
                        return !loginForm;
                    }, { timeout: 10000 });
                    console.log('✅ Successfully navigated away from login page');

                    // Navigate to host details view
                    console.log('🔍 Looking for hosts or navigation...');

                    // Give time for dashboard to load
                    await page.waitForTimeout(3000);

                    // Look for hosts navigation or host entries
                    const hostSelectors = [
                        'a[href*="host"]',
                        'button:has-text("Hosts")',
                        '.host-item',
                        '.MuiTableRow-root',
                        'tr[role="row"]',
                        '[data-testid*="host"]'
                    ];

                    let hostFound = false;
                    for (const selector of hostSelectors) {
                        const hostElement = await page.$(selector);
                        if (hostElement) {
                            console.log(`🎯 Found host element: ${selector}`);
                            await hostElement.click();
                            hostFound = true;
                            break;
                        }
                    }

                    if (hostFound) {
                        console.log('🖱️ Clicked on host element');
                        await page.waitForTimeout(2000);

                        // Look for Info tab
                        const infoSelectors = [
                            'button:has-text("Info")',
                            'tab:has-text("Info")',
                            '.MuiTab-root:has-text("Info")',
                            '[role="tab"]:has-text("Info")'
                        ];

                        for (const selector of infoSelectors) {
                            const infoTab = await page.$(selector);
                            if (infoTab) {
                                console.log(`📋 Found Info tab: ${selector}`);
                                await infoTab.click();
                                console.log('🖱️ Clicked Info tab');
                                await page.waitForTimeout(2000);
                                break;
                            }
                        }
                    } else {
                        console.log('⚠️ No host elements found, staying on current page');
                    }

                } catch (navError) {
                    console.log('⚠️ Still on login page or navigation timeout');
                }

                // Give extra time for content to fully load
                await page.waitForTimeout(3000);
                console.log('✅ Navigation attempt completed!');
            } catch (loginError) {
                console.log('⚠️ Login failed or not needed:', loginError.message);
            }
        }

        // Wait a bit more for dynamic content to load
        await page.waitForTimeout(3000);

        console.log('📸 Taking screenshot...');

        // Take screenshot of the entire page
        const screenshotPath = path.join(__dirname, 'assets', 'images', 'dashboard-screenshot.png');
        await page.screenshot({
            path: screenshotPath,
            fullPage: false, // Just the viewport, not the full scrollable page
            type: 'png'
        });

        console.log(`✅ Screenshot saved to: ${screenshotPath}`);

        // Try to take a cropped version focused on the main content area
        const mainSelectors = [
            '.main-content',
            '.dashboard-container',
            '.container',
            '[class*="dashboard"]',
            '[class*="main"]',
            '.App',
            '#root > div'
        ];

        let croppedTaken = false;
        for (const selector of mainSelectors) {
            const element = await page.$(selector);
            if (element) {
                try {
                    const croppedPath = path.join(__dirname, 'assets', 'images', 'dashboard-preview.png');
                    await element.screenshot({
                        path: croppedPath,
                        type: 'png'
                    });
                    console.log(`✅ Cropped screenshot saved to: ${croppedPath} (using ${selector})`);
                    croppedTaken = true;
                    break;
                } catch (err) {
                    console.log(`⚠️ Failed to screenshot ${selector}:`, err.message);
                }
            }
        }

        if (!croppedTaken) {
            console.log('ℹ️ No suitable element found for cropped screenshot, using full viewport screenshot as preview');
            // Copy the full screenshot as preview
            const fs = require('fs');
            const previewPath = path.join(__dirname, 'assets', 'images', 'dashboard-preview.png');
            fs.copyFileSync(screenshotPath, previewPath);
        }

    } catch (error) {
        console.error('❌ Error capturing screenshot:', error.message);

        // Take a screenshot anyway to see what's happening
        const errorPath = path.join(__dirname, 'assets', 'images', 'error-screenshot.png');
        await page.screenshot({
            path: errorPath,
            fullPage: true,
            type: 'png'
        });
        console.log(`📸 Error screenshot saved to: ${errorPath}`);
    }

    await browser.close();
    console.log('🔒 Browser closed');
}

// Run the screenshot generation
generateDashboardScreenshot().catch(console.error);