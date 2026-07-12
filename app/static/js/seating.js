(() => {
  const root = document.querySelector('[data-seating-root]');
  if (!root) return;

  const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
  const statusBox = document.querySelector('[data-seating-status]');
  let draggedGuestId = null;

  function showStatus(message, type = 'success') {
    if (!statusBox) return;
    statusBox.textContent = message;
    statusBox.className = `share-status ${type}`;
    statusBox.hidden = false;
    window.setTimeout(() => { statusBox.hidden = true; }, 3000);
  }

  async function post(url, payload) {
    const response = await fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
      body: JSON.stringify(payload),
    });
    const data = await response.json().catch(() => ({ ok: false, error: 'תגובה לא תקינה מהשרת.' }));
    if (!response.ok || !data.ok) throw new Error(data.error || 'הפעולה נכשלה.');
    return data;
  }

  async function assign(guestId, tableId) {
    try {
      const data = await post(root.dataset.assignUrl, { guest_id: guestId, table_id: tableId });
      showStatus(data.message);
      window.setTimeout(() => window.location.reload(), 450);
    } catch (error) {
      showStatus(error.message, 'error');
    }
  }

  async function unassign(guestId) {
    try {
      const data = await post(root.dataset.unassignUrl, { guest_id: guestId });
      showStatus(data.message);
      window.setTimeout(() => window.location.reload(), 450);
    } catch (error) {
      showStatus(error.message, 'error');
    }
  }

  document.querySelectorAll('[draggable="true"][data-guest-id]').forEach((card) => {
    card.addEventListener('dragstart', (event) => {
      draggedGuestId = card.dataset.guestId;
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/plain', draggedGuestId);
      card.classList.add('dragging');
    });
    card.addEventListener('dragend', () => card.classList.remove('dragging'));
  });

  document.querySelectorAll('[data-table-id]').forEach((table) => {
    table.addEventListener('dragover', (event) => {
      event.preventDefault();
      table.classList.add('drag-over');
    });
    table.addEventListener('dragleave', () => table.classList.remove('drag-over'));
    table.addEventListener('drop', (event) => {
      event.preventDefault();
      table.classList.remove('drag-over');
      const guestId = event.dataTransfer.getData('text/plain') || draggedGuestId;
      if (guestId) assign(guestId, table.dataset.tableId);
    });
  });

  document.querySelectorAll('[data-mobile-assign]').forEach((select) => {
    select.addEventListener('change', () => {
      if (select.value) assign(select.dataset.guestId, select.value);
    });
  });

  document.querySelectorAll('[data-unassign]').forEach((button) => {
    button.addEventListener('click', () => unassign(button.dataset.guestId));
  });
})();
