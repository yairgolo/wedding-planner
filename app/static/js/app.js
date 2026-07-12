(() => {
  const sidebar = document.querySelector('[data-sidebar]');
  const backdrop = document.querySelector('[data-menu-backdrop]');
  const openButton = document.querySelector('[data-menu-open]');

  if (sidebar && backdrop && openButton) {
    const openMenu = () => {
      sidebar.classList.add('open');
      sidebar.setAttribute('aria-hidden', 'false');
      backdrop.hidden = false;
      document.documentElement.classList.add('menu-open');
      document.body.classList.add('menu-open');
    };

    const closeMenu = () => {
      sidebar.classList.remove('open');
      sidebar.setAttribute('aria-hidden', 'true');
      backdrop.hidden = true;
      document.documentElement.classList.remove('menu-open');
      document.body.classList.remove('menu-open');
    };

    openButton.addEventListener('click', openMenu);
    openButton.addEventListener('pointerup', (event) => {
      if (event.pointerType === 'touch') {
        event.preventDefault();
      }
    });
    backdrop.addEventListener('click', closeMenu);
    sidebar.querySelectorAll('a:not(.disabled)').forEach((link) => link.addEventListener('click', closeMenu));
    document.addEventListener('keydown', (event) => event.key === 'Escape' && closeMenu());
  }

  const sheet = document.querySelector('[data-quick-add-sheet]');
  const sheetBackdrop = document.querySelector('[data-quick-add-backdrop]');
  const quickAddButtons = document.querySelectorAll('[data-quick-add-open]');
  const closeSheetButton = document.querySelector('[data-quick-add-close]');

  if (sheet && sheetBackdrop && quickAddButtons.length) {
    const openSheet = () => {
      sheet.classList.add('open');
      sheet.setAttribute('aria-hidden', 'false');
      sheetBackdrop.hidden = false;
      document.documentElement.classList.add('sheet-open');
    };
    const closeSheet = () => {
      sheet.classList.remove('open');
      sheet.setAttribute('aria-hidden', 'true');
      sheetBackdrop.hidden = true;
      document.documentElement.classList.remove('sheet-open');
    };
    quickAddButtons.forEach((button) => button.addEventListener('click', openSheet));
    closeSheetButton?.addEventListener('click', closeSheet);
    sheetBackdrop.addEventListener('click', closeSheet);
    sheet.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeSheet));
    document.addEventListener('keydown', (event) => event.key === 'Escape' && closeSheet());
  }

  const healthToggle = document.querySelector('[data-health-toggle]');
  const healthChecks = document.querySelector('[data-health-checks]');
  if (healthToggle && healthChecks) {
    healthToggle.addEventListener('click', () => {
      const isOpen = healthToggle.getAttribute('aria-expanded') === 'true';
      healthToggle.setAttribute('aria-expanded', String(!isOpen));
      healthChecks.hidden = isOpen;
      healthToggle.textContent = isOpen ? 'מה מרכיב את הציון?⌄' : 'סגירת הפירוט⌃';
    });
  }

  document.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      const searchInput = document.querySelector('.command-search input');
      if (searchInput) {
        event.preventDefault();
        searchInput.focus();
      }
    }
  });
})();
