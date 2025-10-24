// Minimal, framework-free checkout interactions

(function () {
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => Array.from(root.querySelectorAll(s));

  // Tab switcher
  const tabButtons = $$('.tab-btn');
  const panels = $$('.tab-panel');
  tabButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      tabButtons.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      const tab = btn.dataset.tab;
      panels.forEach((p) => p.classList.remove('show'));
      $(`#tab-${tab}`)?.classList.add('show');
      validateForm(); // re-evaluate CTA enablement per method
    });
  });

  // Quantity & totals
  const qtyInput = $('#qty');
  const unitEl = $('#itemPrice');
  const subtotalEl = $('#subtotal');
  const shippingEl = $('#shipping');
  const grandEl = $('#grand');

  const shippingFlat = 49; // INR
  function toINR(n) {
    return `₹${Number(n).toLocaleString('en-IN')}`;
  }
  function updateTotals() {
    const qty = Math.max(1, parseInt(qtyInput.value || '1', 10));
    const unit = Number(unitEl.dataset.unit || 0);
    const subtotal = qty * unit;
    const grand = subtotal + shippingFlat;
    subtotalEl.textContent = toINR(subtotal);
    shippingEl.textContent = toINR(shippingFlat);
    grandEl.textContent = toINR(grand);
  }
  updateTotals();

  $$('.qty-btn').forEach((b) => {
    b.addEventListener('click', () => {
      const dir = b.dataset.qty;
      let val = Math.max(1, parseInt(qtyInput.value || '1', 10));
      val = dir === 'inc' ? val + 1 : Math.max(1, val - 1);
      qtyInput.value = String(val);
      updateTotals();
    });
  });
  qtyInput.addEventListener('input', updateTotals);

  // ETA (4–7 business days)
  function businessDaysFrom(date, days) {
    const d = new Date(date);
    let added = 0;
    while (added < days) {
      d.setDate(d.getDate() + 1);
      const day = d.getDay();
      if (day !== 0 && day !== 6) added++;
    }
    return d;
  }
  function setEta() {
    const min = businessDaysFrom(new Date(), 4);
    const max = businessDaysFrom(new Date(), 7);
    const fmt = (d) =>
      d.toLocaleDateString('en-IN', { weekday: 'short', month: 'short', day: 'numeric' });
    $('#etaDate').textContent = `${fmt(min)} – ${fmt(max)}`;
  }
  setEta();

  // Enable CTA only when:
  // - Terms checked
  // - Method-specific minimal inputs present
  const agree = $('#agree');
  const payBtn = $('#payBtn');

  function isUPIValid() {
    const id = ($('#upiId')?.value || '').trim();
    // A light format check; real validation happens server-side.
    return /^[\w.\-]{2,}@[A-Za-z]{2,}$/.test(id);
  }
  function isCardValid() {
    const n = ($('#cardNumber')?.value || '').replace(/\s+/g, '');
    const name = ($('#cardName')?.value || '').trim();
    const exp = ($('#cardExpiry')?.value || '').trim();
    const cvv = ($('#cardCvv')?.value || '').trim();
    const okNum = /^\d{13,19}$/.test(n);
    const okName = name.length >= 2;
    const okExp = /^(0[1-9]|1[0-2])\/\d{2}$/.test(exp);
    const okCvv = /^\d{3,4}$/.test(cvv);
    return okNum && okName && okExp && okCvv;
  }
  function isCODValid() {
    const m = ($('#codPhone')?.value || '').replace(/\s+/g, '');
    return /^\+?(\d{10,13})$/.test(m);
  }

  function currentMethod() {
    const active = $('.tab-btn.active')?.dataset.tab || 'upi';
    return active;
  }

  function validateForm() {
    if (!agree.checked) {
      payBtn.disabled = true;
      return;
    }
    const method = currentMethod();
    let ok = false;
    if (method === 'upi') ok = isUPIValid();
    if (method === 'card') ok = isCardValid();
    if (method === 'cod') ok = isCODValid();
    payBtn.disabled = !ok;
  }

  agree.addEventListener('change', validateForm);
  ['input', 'blur'].forEach((evt) => {
    document.addEventListener(evt, (e) => {
      if (
        ['upiId', 'cardNumber', 'cardName', 'cardExpiry', 'cardCvv', 'codPhone'].includes(
          e.target.id
        )
      ) {
        validateForm();
      }
    });
  });

  // Mock submit (replace with real POST + CSRF on integration)
  payBtn.addEventListener('click', () => {
    const method = currentMethod();
    const qty = Math.max(1, parseInt(qtyInput.value || '1', 10));
    const amount = grandEl.textContent;
    alert(`Proceeding with ${method.toUpperCase()} • Qty: ${qty} • Total: ${amount}`);
    // TODO: POST to /checkout/ with CSRF token; server-side validation & gateway init.
  });
})();
