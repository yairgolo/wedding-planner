/* Local end-to-end QA. Start tests/portal_preview.py first.
   No message is sent: native sharing is simulated and external navigation is blocked. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { chromium } = require("playwright");
const base = "http://127.0.0.1:5055/invite-manager";

async function run() {
  const browser = await chromium.launch({ headless: true, channel: process.env.PORTAL_BROWSER_CHANNEL || "msedge" });
  try {
  const artifacts = fs.mkdtempSync(path.join(os.tmpdir(), "invitation-browser-"));
  let checks = 0;
  const passed = message => { checks++; console.log("PASS " + message); };
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  context.setDefaultTimeout(15000);
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.route("https://wa.me/**", route => route.fulfill({ body: "External WhatsApp navigation blocked by QA." }));
  await page.goto(base + "/admin/login");
  await page.getByLabel("אימייל מנהל").fill("qa@example.com");
  await page.getByLabel("סיסמה", { exact: true }).fill("preview-only");
  await page.getByRole("button", { name: "כניסת מנהל" }).click();
  await page.waitForURL(base + "/admin");
  const csrf = await page.locator('input[name="csrf_token"]').first().inputValue();
  for (const id of [1, 3]) await context.request.post(base + `/admin/guest/${id}/status`, { form: { csrf_token: csrf, status: "unsent" } });
  await context.request.post(base + "/admin/senders/1", { form: {
    csrf_token: csrf, name: "אבא של החתן", role: "אבא של החתן", side: "groom", is_active: "y",
    male_template: "{name} היקר, נשמח להזמינך לחתונת בננו.",
    female_template: "{name} היקרה, נשמח להזמינך לחתונת בננו.",
    plural_template: "{name} היקרים, נשמח להזמינכם לחתונת בננו."
  } });
  await page.reload();
  assert(await page.getByRole("navigation").getByRole("link", { name: "שולחים", exact: true }).isVisible());
  assert(await page.getByRole("navigation").getByRole("link", { name: "ההזמנה", exact: true }).isVisible());
  passed("Mobile admin login and visible navigation");

  await page.screenshot({ path: path.join(artifacts, "mobile-dashboard.png"), fullPage: true });
  for (const width of [320, 390, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), "horizontal overflow " + width);
  }
  passed("No dashboard horizontal overflow at 320, 390, 768 and 1280px");
  await page.screenshot({ path: path.join(artifacts, "desktop-dashboard.png"), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });

  await page.getByRole("navigation").getByRole("link", { name: "שולחים", exact: true }).click();
  assert(await page.getByRole("button", { name: "העתקת קישור" }).first().isVisible());
  await page.getByRole("button", { name: "העתקת קישור" }).first().click();
  await page.getByRole("status").filter({ hasText: "הועתק" }).waitFor({ state: "visible" });
  passed("Existing senders page and copy personal link");
  const senderCard = page.locator(".sender-card").filter({ hasText: "אבא של החתן" });
  await senderCard.getByRole("link", { name: "עריכת נוסח ופרטים" }).click();
  assert(await page.getByRole("heading", { name: "עריכת הנוסח של אבא של החתן" }).isVisible());
  assert.equal(await page.locator(".sender-card").count(), 0);
  await page.getByLabel("נוסח לזכר", { exact: true }).fill("{name} היקר, נשמח לחגוג יחד בחתונת בננו.");
  await page.getByLabel("נוסח לנקבה", { exact: true }).fill("{name} היקרה, נשמח לחגוג יחד בחתונת בננו.");
  await page.getByLabel("נוסח לרבים", { exact: true }).fill("{name} היקרים, נשמח לחגוג יחד בחתונת בננו.");
  await page.getByRole("button", { name: "שמירת הנוסחים והפרטים" }).click();
  await page.waitForURL(base + "/admin/senders");
  await page.locator(".sender-card").filter({ hasText: "אבא של החתן" }).getByRole("link", { name: "עריכת נוסח ופרטים" }).click();
  assert.equal(await page.getByLabel("נוסח לזכר", { exact: true }).inputValue(), "{name} היקר, נשמח לחגוג יחד בחתונת בננו.");
  passed("Admin edits and persists all three templates in dedicated sender form");
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1));
  await page.goto(base + "/admin/settings");
  assert(await page.getByAltText("תמונת ההזמנה הנוכחית").isVisible());
  await page.screenshot({ path: path.join(artifacts, "mobile-settings.png"), fullPage: true });
  passed("Mobile image settings page");

  await page.goto(base + "/admin/guest/new");
  await page.getByLabel("שם פרטי / פנייה").fill("אורחת בדיקה");
  // Browser validation must prevent a silent default gender.
  await page.getByRole("button", { name: "שמירת מוזמן" }).click();
  assert(page.url().endsWith("/guest/new"));
  await page.getByLabel("צורת פנייה").selectOption("female");
  await page.getByRole("button", { name: "שמירת מוזמן" }).click();
  await page.waitForURL(base + "/admin");
  passed("Create guest on mobile with first name and salutation only");
  const noPhone = page.locator(".guest").filter({ hasText: "ללא טלפון בדיקה" });
  await noPhone.getByRole("button", { name: "שליחת הזמנה" }).click();
  await page.locator("#previewArea").waitFor({ state: "visible" });
  assert((await page.locator("#openWhatsapp").getAttribute("href")).startsWith("https://wa.me/?text="));
  assert((await page.locator("#dialogPhone").textContent()).includes("בחירת הנמען"));
  await page.locator("#cancelSend").click();
  await page.waitForLoadState("networkidle");
  passed("Sharing without phone works and offers recipient selection in WhatsApp");

  const guest = () => page.locator(".guest").filter({ hasText: "משה לוי" });
  await page.evaluate(() => Object.defineProperty(navigator, "share", { configurable: true, value: undefined }));
  await guest().getByRole("button", { name: "שליחת הזמנה" }).click();
  await page.locator("#previewArea").waitFor({ state: "visible" });
  // Desktop Chromium has no native file share: fallback must be usable.
  assert(await page.locator("#fallbackHelp").isVisible());
  assert((await page.locator("#openWhatsapp").getAttribute("href")).startsWith("https://wa.me/972501234567?text="));
  assert(await page.locator("#downloadImage").isVisible());
  assert(!(await page.locator("#confirmArea").isVisible()));
  await page.screenshot({ path: path.join(artifacts, "mobile-share-fallback.png"), fullPage: true });
  await page.locator("#cancelSend").click();
  await page.waitForLoadState("networkidle");
  assert((await guest().locator(".status").textContent()).includes("טרם"));
  passed("Text-to-recipient and image download fallback; cancel restores status");

  // Install a deterministic native-share mock; preserve real user activation checks.
  await context.addInitScript(() => {
    Object.defineProperty(navigator, "canShare", { configurable: true, value: data => data.files?.length === 1 });
    Object.defineProperty(navigator, "share", { configurable: true, value: async data => {
      window.lastShare = { text: data.text, size: data.files[0].size, type: data.files[0].type,
                           active: navigator.userActivation.isActive };
      if (window.abortShare) throw new DOMException("Cancelled", "AbortError");
    } });
  });
  await page.reload();
  await guest().getByRole("button", { name: "שליחת הזמנה" }).click();
  await page.locator("#previewArea").waitFor({ state: "visible" });
  await page.locator("#sendAs").selectOption("1");
  await page.waitForFunction(() => document.querySelector("#messagePreview").textContent.includes("בננו")
    && !document.querySelector("#shareButton").disabled);
  assert(!(await page.locator("#fallbackHelp").isVisible()));
  await page.locator("#shareButton").click();
  await page.locator("#confirmArea").waitFor({ state: "visible" });
  const shared = await page.evaluate(() => window.lastShare);
  assert(shared.active, "native share lost transient user activation");
  assert(shared.text.includes("משה היקר") && shared.text.includes("בננו"));
  assert(shared.size > 0 && shared.type === "image/jpeg");
  await page.screenshot({ path: path.join(artifacts, "mobile-share-confirm.png") });
  await page.getByRole("button", { name: "כן, שלחתי את ההזמנה" }).click();
  await page.waitForLoadState("networkidle");
  assert((await guest().locator(".status").textContent()).includes("נשלח"));
  passed("Admin chooses sender, native share carries text+image with user activation, explicit confirmation");

  await page.evaluate(() => { window.abortShare = true; });
  await guest().getByRole("button", { name: "שליחה נוספת" }).click();
  await page.locator("#previewArea").waitFor({ state: "visible" });
  await page.locator("#shareButton").click();
  await page.waitForLoadState("networkidle");
  await page.locator("#sendDialog").waitFor({ state: "hidden" });
  assert((await guest().locator(".status").textContent()).includes("נשלח"));
  passed("Native share cancellation preserves earlier sent status");

  await page.goto(base + "/u/qa-groom");
  assert(await page.getByRole("link", { name: "הנוסח שלי", exact: true }).isVisible());
  assert(!(await page.locator(".guest").filter({ hasText: "מרים כהן" }).count()));
  const pair = () => page.locator(".guest").filter({ hasText: "יצחק והילה" });
  await pair().getByRole("button", { name: "שליחת הזמנה" }).click();
  await page.locator("#previewArea").waitFor({ state: "visible" });
  assert((await page.locator("#messagePreview").textContent()).startsWith("יצחק והילה היקרים"));
  await page.reload();
  await pair().getByRole("button", { name: "המשך טיפול" }).click();
  await page.locator("#confirmArea").waitFor({ state: "visible" });
  await page.getByRole("button", { name: "לא נשלח — ביטול הפעולה" }).click();
  await page.waitForLoadState("networkidle");
  assert((await pair().locator(".status").textContent()).includes("טרם"));
  passed("Sender sees only own side, plural greeting and resume after refresh");

  await page.getByRole("link", { name: "הנוסח שלי", exact: true }).click();
  await page.getByLabel("נוסח לזכר").fill("{name} שלום, מחכים לחגוג יחד!");
  await page.getByRole("button", { name: "שמירת הנוסחים שלי" }).click();
  await page.waitForURL(base + "/u/qa-groom");
  passed("Sender edits own templates on mobile");
  await pair().getByRole("button", { name: "? סימון בסימן שאלה", exact: true }).click();
  await page.waitForLoadState("networkidle");
  assert(await pair().locator(".send-button").isDisabled());
  assert(await pair().locator(".decision-note").isVisible());
  await pair().getByRole("button", { name: "כן, מזמינים", exact: true }).click();
  await page.waitForLoadState("networkidle");
  assert(await pair().locator(".send-button").isEnabled());
  passed("Question mark blocks sending until explicitly inviting again");
  await pair().locator("summary").click();
  page.once("dialog", dialog => dialog.dismiss());
  await pair().getByRole("button", { name: "מחיקת מוזמן", exact: true }).click();
  assert(await pair().isVisible());
  page.once("dialog", dialog => dialog.accept());
  await pair().getByRole("button", { name: "מחיקת מוזמן", exact: true }).click();
  await page.waitForLoadState("networkidle");
  assert.equal(await pair().count(), 0);
  await page.getByRole("link", { name: "מוזמנים שנמחקו", exact: true }).click();
  await pair().getByRole("button", { name: "שחזור מוזמן", exact: true }).click();
  await page.waitForLoadState("networkidle");
  assert(await pair().locator(".send-button").isEnabled());
  passed("Mobile delete requires confirmation and supports restoring guest");
  await page.locator(".excel-tools summary").click();
  await page.locator("#excelFile").setInputFiles({
    name: "partial.csv", mimeType: "text/csv",
    buffer: Buffer.from("שם פרטי\nייבוא חלקי\n", "utf8")
  });
  await page.getByRole("button", { name: "ייבוא קובץ", exact: true }).click();
  await page.waitForLoadState("networkidle");
  const partial = () => page.locator(".guest").filter({ hasText: "ייבוא חלקי" }).last();
  assert(await partial().locator(".send-button").isDisabled());
  assert((await partial().textContent()).includes("חסרה צורת פנייה"));
  await partial().getByRole("link", { name: "עריכה", exact: true }).click();
  await page.getByLabel("צורת פנייה", { exact: true }).selectOption("male");
  await page.getByRole("button", { name: "שמירת מוזמן", exact: true }).click();
  await page.waitForLoadState("networkidle");
  assert(await partial().locator(".send-button").isEnabled());
  passed("Partial CSV import blocks sending until salutation is completed on mobile");
  assert.deepEqual(errors, []);
  passed("No uncaught browser JavaScript errors");
  console.log(JSON.stringify({ checks, artifacts }));
  } finally { await browser.close(); }
}
run().catch(error => { console.error(error); process.exit(1); });
