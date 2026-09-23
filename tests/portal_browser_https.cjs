/* Run against tests/portal_preview.py. Browser requests use an HTTPS origin and
   are forwarded locally with ProxyFix headers, as at the production reverse proxy.
   Referrer generation is performed by the browser, never manually supplied.
   No traffic is sent to the example domains or to WhatsApp. */
const assert = require("node:assert/strict");
const { chromium } = require("playwright");
const origin = "https://portal.example.test";
const root = origin + "/invite-manager";

async function run() {
  const browser = await chromium.launch({
    headless: true, channel: process.env.PORTAL_BROWSER_CHANNEL || "msedge"
  });
  try {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
    context.setDefaultTimeout(15000);
    const page = await context.newPage();
    const posts = [];
    await context.route(origin + "/**", async route => {
      const request = route.request();
      const headers = { ...request.headers(),
        "x-forwarded-proto": "https", "x-forwarded-host": "portal.example.test", "x-forwarded-port": "443" };
      delete headers.host;
      const response = await context.request.fetch(
        request.url().replace(origin, "http://127.0.0.1:5055"), {
          method: request.method(), headers, data: request.postDataBuffer() || undefined,
          maxRedirects: 0
        }
      );
      if (request.method() === "POST") posts.push({
        url: request.url(), referer: request.headers().referer, status: response.status()
      });
      await route.fulfill({ response });
    });
    await page.goto(root + "/admin/login");
    await page.getByLabel("אימייל מנהל").fill("qa@example.com");
    await page.getByLabel("סיסמה", { exact: true }).fill("preview-only");
    await page.getByRole("button", { name: "כניסת מנהל" }).click();
    await page.waitForURL(root + "/admin");
    console.log("PASS HTTPS admin login form with browser-generated Referer");

    await page.goto(root + "/admin/guest/1/edit");
    await page.getByRole("button", { name: "שמירת מוזמן" }).click();
    await page.waitForURL(root + "/admin");
    console.log("PASS HTTPS admin edit form");

    await page.locator('.guest[data-guest-row="1"]').getByRole("button").first().click();
    await page.locator("#previewArea").waitFor({ state: "visible" });
    await page.locator("#cancelSend").click();
    await page.waitForLoadState("networkidle");
    console.log("PASS HTTPS admin prepare and cancel AJAX");

    await page.goto(root + "/u/qa-groom/guest/1/edit");
    await page.getByRole("button", { name: "שמירת מוזמן" }).click();
    await page.waitForURL(root + "/u/qa-groom");
    await page.locator('.guest[data-guest-row="1"]').getByRole("button").first().click();
    await page.locator("#previewArea").waitFor({ state: "visible" });
    await page.locator("#cancelSend").click();
    await page.waitForLoadState("networkidle");
    console.log("PASS HTTPS sender edit, prepare and cancel");

    assert.equal(posts.length, 7);
    for (const post of posts) {
      assert(post.referer?.startsWith(root), JSON.stringify(post));
      assert([200, 302].includes(post.status), JSON.stringify(post));
    }
    let externalReferrer;
    await context.route("https://outside.example.test/**", async route => {
      externalReferrer = route.request().headers().referer;
      await route.fulfill({ body: "<h1>Local privacy test</h1>", contentType: "text/html" });
    });
    await page.evaluate(() => {
      const link = document.createElement("a");
      link.href = "https://outside.example.test/";
      link.textContent = "Privacy check";
      document.body.append(link);
    });
    await page.getByRole("link", { name: "Privacy check" }).click();
    await page.waitForURL("https://outside.example.test/");
    assert.equal(externalReferrer, undefined);
    console.log("PASS External navigation does not disclose the personal link");
    console.log("HTTPS referrer regression checks passed: 7 writes and external privacy.");
  } finally { await browser.close(); }
}
run().catch(error => { console.error(error); process.exit(1); });
