(() => {
  const config = window.invitationConfig;
  if (!config) return;

  const guestData = new Map();
  let preparedPngBlob = null;
  const statusBox = document.querySelector("[data-share-status]");
  const shareButtons = [...document.querySelectorAll("[data-share-guest]")];

  function endpoint(template, guestId) {
    return template.replace(/\/0(?=\/|$)/, `/${guestId}`);
  }

  function showStatus(message, type = "info") {
    if (!statusBox) return;
    statusBox.hidden = false;
    statusBox.textContent = message;
    statusBox.className = `share-status ${type}`;
    window.setTimeout(() => { statusBox.hidden = true; }, 4500);
  }

  async function fetchGuestData(guestId) {
    const response = await fetch(endpoint(config.shareDataUrl, guestId), {
      headers: { "Accept": "application/json" },
      credentials: "same-origin"
    });
    if (!response.ok) throw new Error("לא ניתן לטעון את פרטי ההזמנה");
    return response.json();
  }

  async function imageToPngBlob(imageUrl) {
    const safeImageUrl = new URL(imageUrl, window.location.origin);
    if (window.location.protocol === "https:" && safeImageUrl.protocol === "http:") {
      safeImageUrl.protocol = "https:";
    }

    const response = await fetch(safeImageUrl.toString(), {
      cache: "no-store",
      credentials: "same-origin"
    });
    if (!response.ok) throw new Error("תמונת ההזמנה אינה זמינה");
    const sourceBlob = await response.blob();
    const bitmap = await createImageBitmap(sourceBlob);
    const canvas = document.createElement("canvas");
    canvas.width = bitmap.width;
    canvas.height = bitmap.height;
    const context = canvas.getContext("2d");
    context.drawImage(bitmap, 0, 0);
    bitmap.close();
    return new Promise((resolve, reject) => {
      canvas.toBlob(blob => blob ? resolve(blob) : reject(new Error("יצירת PNG נכשלה")), "image/png", 0.95);
    });
  }

  async function prepareSharing() {
    if (!shareButtons.length) return;
    shareButtons.forEach(button => {
      if (!button.disabled) {
        button.disabled = true;
        button.dataset.originalLabel = button.textContent;
        button.textContent = "מכין שיתוף...";
      }
    });
    try {
      const firstId = shareButtons[0].dataset.shareGuest;
      const firstData = await fetchGuestData(firstId);
      guestData.set(firstId, firstData);
      if (!firstData.image_url) throw new Error("לא הועלתה תמונת הזמנה");
      preparedPngBlob = await imageToPngBlob(firstData.image_url);
      await Promise.all(shareButtons.slice(1).map(async button => {
        const id = button.dataset.shareGuest;
        guestData.set(id, await fetchGuestData(id));
      }));
      shareButtons.forEach(button => {
        button.disabled = false;
        button.textContent = button.dataset.originalLabel || "שליחת הזמנה";
      });
    } catch (error) {
      console.error(error);
      shareButtons.forEach(button => {
        button.disabled = true;
        button.textContent = "השיתוף לא זמין";
      });
      showStatus(error.message || "הכנת השיתוף נכשלה", "error");
    }
  }

  async function markShared(guestId, activityType) {
    const body = new URLSearchParams({ type: activityType, csrf_token: config.csrfToken });
    const response = await fetch(endpoint(config.markSharedUrl, guestId), {
      method: "POST",
      body,
      credentials: "same-origin",
      headers: { "Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded" }
    });
    if (!response.ok) throw new Error("השיתוף הצליח אך המעקב לא עודכן");
    return response.json();
  }

  function shareInvitation(button) {
    const guestId = button.dataset.shareGuest;
    const activityType = button.dataset.activityType || "sent";
    const data = guestData.get(guestId);
    if (!data || !preparedPngBlob) {
      showStatus("השיתוף עדיין בהכנה. נסה שוב בעוד רגע.", "error");
      return;
    }
    if (!window.isSecureContext) {
      showStatus("יש לפתוח את האתר דרך HTTPS.", "error");
      return;
    }
    if (!navigator.share) {
      showStatus("הדפדפן אינו תומך בשיתוף קבצים.", "error");
      return;
    }

    const safeName = data.name.replace(/[^\p{L}\p{N}-]+/gu, "-");
    const file = new File([preparedPngBlob], `wedding-invitation-${safeName}.png`, {
      type: "image/png"
    });
    if (navigator.canShare && !navigator.canShare({ files: [file] })) {
      showStatus("המכשיר אינו מאפשר לשתף את קובץ התמונה.", "error");
      return;
    }

    // navigator.share is called synchronously inside the click handler so iOS keeps
    // the user-activation permission. All image processing happened during page load.
    const sharePromise = navigator.share({
      files: [file],
      title: "הזמנה לחתונה",
      text: data.text
    });
    button.disabled = true;
    sharePromise
      .then(() => markShared(guestId, activityType))
      .then(() => {
        showStatus(activityType === "reminder" ? "התזכורת שותפה והמעקב עודכן." : "ההזמנה שותפה והמעקב עודכן.", "success");
        window.setTimeout(() => window.location.reload(), 650);
      })
      .catch(error => {
        if (error.name === "AbortError") showStatus("השיתוף בוטל.");
        else {
          console.error(error);
          showStatus(error.message || "השיתוף נכשל", "error");
        }
      })
      .finally(() => { button.disabled = false; });
  }

  async function copyInvitation(button) {
    try {
      const id = button.dataset.copyGuest;
      const data = guestData.get(id) || await fetchGuestData(id);
      guestData.set(id, data);
      await navigator.clipboard.writeText(data.text);
      showStatus("טקסט ההזמנה הועתק ללוח.", "success");
    } catch (error) {
      showStatus(error.message || "העתקת הטקסט נכשלה", "error");
    }
  }

  shareButtons.forEach(button => {
    button.addEventListener("click", () => shareInvitation(button));
  });
  document.querySelectorAll("[data-copy-guest]").forEach(button => {
    button.addEventListener("click", () => copyInvitation(button));
  });
  prepareSharing();
})();
