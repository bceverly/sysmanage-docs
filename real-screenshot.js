#!/usr/bin/env node
// Copyright (c) 2024-2026 Bryan Everly
// Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
// See the LICENSE file in the project root for the full terms.


const { chromium } = require('playwright');
const path = require('path');

async function captureRealSysManage() {
    console.log('🚀 Starting browser for REAL SysManage screenshot...');

    const browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-dev-shm-usage']
    });

    const page = await browser.newPage();
    await page.setViewportSize({ width: 1400, height: 900 });

    try {
        console.log('📱 Navigating to SysManage...');

        // Navigate to SysManage
        await page.goto('http://t14.theeverlys.com:3000', {
            waitUntil: 'networkidle',
            timeout: 30000
        });

        console.log('⏳ Waiting for page to load...');
        await page.waitForTimeout(3000);

        // Take a screenshot of whatever we get
        console.log('📸 Taking initial screenshot...');
        await page.screenshot({
            path: path.join(__dirname, 'assets', 'images', 'debug-initial.png'),
            fullPage: false,
            type: 'png'
        });

        // Try to find login form
        try {
            await page.waitForSelector('input[name="userid"]', { timeout: 5000 });
            console.log('🔑 Found login form, attempting login...');

            // Fill login form with demo user
            await page.fill('input[name="userid"]', 'demo@example.com');
            await page.fill('input[name="password"]', 'SimpleDemo123');

            console.log('📧 Filled credentials, clicking login...');

            // Click login button
            await page.click('button[type="submit"]');

            console.log('✅ Login completed, waiting for dashboard...');
            await page.waitForTimeout(5000);

            // Take screenshot after login
            console.log('📸 Taking post-login screenshot...');
            await page.screenshot({
                path: path.join(__dirname, 'assets', 'images', 'debug-after-login.png'),
                fullPage: false,
                type: 'png'
            });

            // Try to navigate to hosts
            console.log('🔗 Navigating to hosts page...');
            await page.goto('http://t14.theeverlys.com:3000/hosts', {
                waitUntil: 'networkidle',
                timeout: 15000
            });

            await page.waitForTimeout(3000);

            // Take final screenshot
            console.log('📸 Taking hosts page screenshot...');
            await page.screenshot({
                path: path.join(__dirname, 'assets', 'images', 'dashboard-screenshot.png'),
                fullPage: false,
                type: 'png'
            });

            console.log('✅ Real screenshot captured!');

        } catch (loginError) {
            console.log('⚠️ Login process failed:', loginError.message);

            // Take a screenshot of whatever state we're in
            await page.screenshot({
                path: path.join(__dirname, 'assets', 'images', 'dashboard-screenshot.png'),
                fullPage: false,
                type: 'png'
            });
        }

    } catch (error) {
        console.error('❌ Error:', error.message);

        // Take error screenshot
        await page.screenshot({
            path: path.join(__dirname, 'assets', 'images', 'error-screenshot.png'),
            fullPage: true,
            type: 'png'
        });
    }

    await browser.close();
    console.log('🔒 Browser closed');
}

// Run the capture
captureRealSysManage().catch(console.error);