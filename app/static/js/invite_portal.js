(() => {
  "use strict";
  const toast = (message) => {
    const element = document.querySelector("#toast");
    if (!element) return;
    element.textContent = message;
    element.hidden = false;
    window.setTimeout(() => { element.hidden = true; }, 4500);
  };
  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      try { await navigator.clipboard.writeText(text); toast("הועתק בהצלחה"); return; }
      catch { /* Older browsers can still use a selection-based copy. */ }
    }
    const area = document.createElement("textarea");
    area.value = text;
    document.body.append(area);
    area.select();
    const copied = document.execCommand("copy");
    area.remove();
    toast(copied ? "הועתק בהצלחה" : "לא הצלחנו להעתיק. סמנו את הטקסט והעתיקו ידנית.");
  }
  document.querySelectorAll("[data-copy-target]").forEach(button => {
    button.addEventListener("click", () => copyText(document.getElementById(button.dataset.copyTarget).value));
  });
  document.querySelectorAll("[data-confirm-prompt]").forEach(form => {
    form.addEventListener("submit", event => {
      if (!window.confirm(form.dataset.confirmPrompt)) event.preventDefault();
    });
  });

  const configElement = document.querySelector("#portalConfig");
  if (!configElement) return;
  const config = JSON.parse(configElement.textContent);
  const dialog = document.querySelector("#sendDialog");
  const preview = document.querySelector("#previewArea");
  const textPreview = document.querySelector("#messagePreview");
  const title = document.querySelector("#dialogName");
  const phone = document.querySelector("#dialogPhone");
  const errorBox = document.querySelector("#sendError");
  const shareButton = document.querySelector("#shareButton");
  const confirmArea = document.querySelector("#confirmArea");
  const senderSelect = document.querySelector("#sendAs");
  const cancelButton = document.querySelector("#cancelSend");
  let guestId = null, data = null, imageFile = null, busy = false, shareLaunched = false;

  function endpoint(template) {
    return template.replace(/\/0(?=\/|$)/, "/" + guestId);
  }
  function showError(message) {
    errorBox.textContent = message;
    errorBox.hidden = false;
  }
  function setBusy(value) {
    busy = value;
    dialog.setAttribute("aria-busy", String(value));
    dialog.querySelectorAll("button, select").forEach(button => { button.disabled = value; });
  }
  async function post(url, values) {
    const response = await fetch(url, {
      method: "POST", credentials: "same-origin",
      headers: { "Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ ...values, csrf_token: config.csrf })
    });
    const isJson = (response.headers.get("content-type") || "").includes("application/json");
    const result = isJson ? await response.json() : null;
    if (!response.ok || !result || !result.ok) {
      const fallback = response.status === 400
        ? "הפעולה לא הושלמה. ייתכן שהחיבור פג — רעננו את העמוד ונסו שוב."
        : "לא הצלחנו להשלים את הפעולה. בדקו את החיבור ונסו שוב.";
      throw new Error(result?.error || fallback);
    }
    return result;
  }
  async function cancelAttempt() {
    if (!data?.attempt) return;
    await post(endpoint(config.confirmUrl), { attempt: data.attempt, sent: "false" });
    data = null;
  }
  async function prepare() {
    setBusy(true);
    errorBox.hidden = true;
    preview.hidden = true;
    confirmArea.hidden = true;
    cancelButton.hidden = false;
    imageFile = null;
    try {
      data = await post(endpoint(config.prepareUrl), { sender_id: senderSelect?.value || "" });
      title.textContent = data.name;
      phone.textContent = data.phone + " · נוסח: " + data.sender_name;
      textPreview.textContent = data.text;
      const response = await fetch(data.image_url, { credentials: "same-origin", cache: "no-store" });
      if (!response.ok) throw new Error("לא ניתן לטעון את תמונת ההזמנה. נסו שוב או עדכנו את המנהל.");
      const blob = await response.blob();
      imageFile = new File([blob], "wedding-invitation.jpg", { type: "image/jpeg" });
      document.querySelector("#dialogImage").src = data.image_url;
      document.querySelector("#downloadImage").href = data.image_url;
      document.querySelector("#openWhatsapp").href =
        "https://wa.me/" + data.whatsapp_phone + "?text=" + encodeURIComponent(data.text);
      preview.hidden = false;
      shareLaunched = false;
      const supported = window.isSecureContext && typeof navigator.share === "function"
        && typeof navigator.canShare === "function" && navigator.canShare({ files: [imageFile] });
      shareButton.hidden = !supported;
      document.querySelector("#fallbackHelp").hidden = supported;
      document.querySelector("#manualShare").open = !supported;
      // A pending invitation survives refresh or switching to WhatsApp.
      confirmArea.hidden = !data.resumed;
      if (data.resumed) toast("נמצאה הזמנה בטיפול. אפשר לאשר שליחה או לבטל.");
    } catch (error) {
      showError(error.message);
    } finally {
      setBusy(false);
    }
  }
  document.querySelectorAll(".send-button").forEach(button => {
    button.addEventListener("click", async () => {
      if (busy || dialog.open) return;
      guestId = button.dataset.guest;
      data = null;
      shareLaunched = false;
      title.textContent = button.closest(".guest").querySelector("h3").textContent;
      phone.textContent = "מכינים את התמונה והטקסט…";
      if (senderSelect) {
        document.querySelector("#senderChoice").hidden = false;
        senderSelect.value = "";
        const side = button.closest(".guest").dataset.side;
        [...senderSelect.options].forEach(option => {
          option.disabled = Boolean(option.dataset.side && option.dataset.side !== side);
          option.hidden = option.disabled;
        });
      }
      dialog.showModal(); // Feedback appears before any network work.
      await prepare();
    });
  });
  senderSelect?.addEventListener("change", async () => {
    if (busy) return;
    setBusy(true);
    try { await cancelAttempt(); }
    catch (error) { showError(error.message); setBusy(false); return; }
    await prepare();
  });
  shareButton.addEventListener("click", () => {
    if (busy || !imageFile || !data) return;
    errorBox.hidden = true;
    // This call is directly inside the click handler, with no preceding await.
    // iOS requires that user activation is still active when share() is invoked.
    try {
      const sharing = navigator.share({ files: [imageFile], text: data.text, title: "הזמנה לחתונה" });
      shareLaunched = true;
      preview.hidden = true;
      if (senderSelect) document.querySelector("#senderChoice").hidden = true;
      confirmArea.hidden = false;
      cancelButton.hidden = true;
      dialog.scrollTop = 0;
      shareButton.disabled = true;
      Promise.resolve(sharing).catch(async error => {
        if (error.name === "AbortError") {
          try { await cancelAttempt(); window.location.reload(); }
          catch (failure) { showError(failure.message); }
        } else {
          preview.hidden = false;
          showError("השיתוף לא נפתח: " + error.message + ". אפשר להשתמש באפשרות הצירוף הידני.");
          document.querySelector("#manualShare").open = true;
        }
      }).finally(() => { shareButton.disabled = false; });
    } catch (error) {
      preview.hidden = false;
      showError("לא ניתן לפתוח שיתוף במכשיר הזה. השתמשו באפשרות הצירוף הידני.");
      document.querySelector("#manualShare").open = true;
    }
  });
  document.querySelector("#copyMessage").addEventListener("click", () => copyText(data?.text || ""));
  document.querySelector("#openWhatsapp").addEventListener("click", () => {
    shareLaunched = true;
    confirmArea.hidden = false;
    confirmArea.scrollIntoView({ block: "nearest" });
  });
  document.querySelectorAll("[data-confirm]").forEach(button => {
    button.addEventListener("click", async () => {
      if (busy || !data) return;
      setBusy(true);
      try {
        await post(endpoint(config.confirmUrl), { attempt: data.attempt, sent: button.dataset.confirm });
        window.location.reload();
      } catch (error) { showError(error.message); setBusy(false); }
    });
  });
  async function close(cancelExplicitly = false) {
    if (busy) return;
    if (shareLaunched && !cancelExplicitly) {
      // Keep it pending when the user closes without saying whether they sent.
      window.location.reload();
      return;
    }
    setBusy(true);
    try {
      const hadAttempt = Boolean(data?.attempt);
      await cancelAttempt();
      dialog.close();
      if (hadAttempt) window.location.reload();
    } catch (error) { showError(error.message); }
    finally { setBusy(false); }
  }
  document.querySelector("[data-close]").addEventListener("click", () => close());
  cancelButton.addEventListener("click", () => close(true));
  dialog.addEventListener("cancel", event => { event.preventDefault(); close(); });
})();
