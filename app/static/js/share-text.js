(() => {
  const readText = (selector) => document.querySelector(selector)?.value || "";
  document.querySelectorAll("[data-copy-text]").forEach((button) => {
    button.addEventListener("click", async () => {
      const text = readText(button.dataset.copyText);
      try {
        await navigator.clipboard.writeText(text);
        button.textContent = "✓ הועתק";
        setTimeout(() => (button.textContent = "📋 העתקה"), 1800);
      } catch (_) {
        alert("לא הצלחנו להעתיק. ניתן לסמן את הטקסט ידנית.");
      }
    });
  });
  document.querySelectorAll("[data-native-share]").forEach((button) => {
    button.addEventListener("click", async () => {
      const text = readText(button.dataset.nativeShare);
      if (!navigator.share) return alert("שיתוף ישיר אינו נתמך בדפדפן הזה.");
      try { await navigator.share({ text }); } catch (error) {
        if (error.name !== "AbortError") alert("השיתוף לא הצליח.");
      }
    });
  });
})();
