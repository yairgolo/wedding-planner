(() => {
  const sidebar = document.querySelector('[data-sidebar]');
  const backdrop = document.querySelector('[data-menu-backdrop]');
  const openButton = document.querySelector('[data-menu-open]');

  if (!sidebar || !backdrop || !openButton) return;

  const openMenu = () => {
    sidebar.classList.add('open');
    sidebar.setAttribute('aria-hidden', 'false');
    backdrop.hidden = false;
    document.documentElement.classList.add('menu-open');
  };

  const closeMenu = () => {
    sidebar.classList.remove('open');
    sidebar.setAttribute('aria-hidden', 'true');
    backdrop.hidden = true;
    document.documentElement.classList.remove('menu-open');
  };

  openButton.addEventListener('click', openMenu);
  backdrop.addEventListener('click', closeMenu);
  sidebar.querySelectorAll('a:not(.disabled)').forEach((link) => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', (event) => event.key === 'Escape' && closeMenu());
})();
