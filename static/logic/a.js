// HiveFusion Lab - Cybersecurity Tools for Everyone
// Copyright © 2025 HiveFusion Lab.
// All rights reserved.

// Website: https://www.hivefusion.in
// License: Proprietary Unauthorized copying, modification, or distribution of this file is strictly prohibited without written consent.
// Author: HiveFusion Lab Development Team

const mainImage = document.getElementById('pocket-mini-main-image');
const thumbnails = document.querySelectorAll('.product__pocket__mini__thumbnail');
const counters = document.querySelectorAll('.count');
const hamburger = document.querySelector('.show--mobile');
const mobileMenu = document.querySelector('.mobile-menu');
const closeBtn = document.getElementById('closeMenu');
const ContactHome = document.getElementById('contact-form')

hamburger.addEventListener('click', () => {
    mobileMenu.classList.remove('hidden');
    document.body.classList.add('menu-open');
});

closeBtn.addEventListener('click', () => {
    mobileMenu.classList.add('hidden');
    document.body.classList.remove('menu-open');
});

function qs(root, sel) { return (root || document).querySelector(sel); }
function qsa(root, sel) { return Array.from((root || document).querySelectorAll(sel)); }

function defaultOptions() {
    return {
        debug: false,           // set true for console logs during development
        ajaxSubmit: true,      // if true, module will POST JSON to form.action instead of normal submit
        ajaxHeaders: {},        // extra headers for AJAX
        selectors: {
            form: '.form',
            submitButton: 'button[type="submit"]',
            checkboxes: '.hf-checkbox__input', // both checkboxes share class
            errorContainer: '#address_errors'  // must exist or module will create one
        },
        validation: {
            require_address_presence: true, // require at least some address fields
        }
    };
}


/* ---------- Validators ---------- */
const validators = {
    email: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v || '').trim()),
    phone: (v) => {
        if (!v) return false;
        const s = String(v).replace(/\s+/g, '').replace(/^\+91/, '');
        return /^[6-9]\d{9}$/.test(s);
    },
    pincode: (v) => /^\d{6}$/.test(String(v || '').trim()),
    nonempty: (v) => String(v || '').trim().length > 0
};

/* ---------- Utility: shallow diff ---------- */
function diffObjects(orig = {}, curr = {}) {
    const changed = {};
    for (const k of Object.keys(curr)) {
        const o = (orig[k] === undefined || orig[k] === null) ? '' : String(orig[k]);
        const c = (curr[k] === undefined || curr[k] === null) ? '' : String(curr[k]);
        if (o !== c) changed[k] = { old: orig[k] ?? '', new: curr[k] ?? '' };
    }
    return changed;
}

/* ---------- Build address object from form inputs ---------- */
function buildAddressFromForm(form) {
    const map = (name) => qs(form, `[name="${name}"]`)?.value?.trim() ?? '';
    return {
        fname: map('fname'),
        lname: map('lname'),
        phone: map('phone'),
        flat: map('flat'),
        address: map('address'),
        city: map('city'),
        state: map('state'),
        pincode: map('pincode'),
        landmark: map('landmark'),
        email: map('email')
    };
}

/* ---------- Accessibility helpers ---------- */
function ensureErrorContainer(form, selector) {
    // Defensive default
    if (!selector || typeof selector !== 'string') selector = '#address_errors';

    // Normalize: if just an id without '#', add it
    if (!selector.startsWith('#') && !selector.startsWith('.')) {
        selector = `#${selector}`;
    }

    let container = qs(form, selector);

    // If the selector refers to an ID but wasn't found inside the form,
    // try finding it in the document as a fallback.
    if (!container && selector.startsWith('#')) {
        container = document.getElementById(selector.slice(1));
    }

    // Create the container if it still doesn't exist
    if (!container) {
        container = document.createElement('div');
        // If selector was an ID (e.g. "#address_errors"), set that id; otherwise generate one
        const idName = selector.startsWith('#') ? selector.slice(1) : `address_errors_${Math.random().toString(36).slice(2, 8)}`;
        container.id = idName;
        container.setAttribute('aria-live', 'polite');
        container.className = 'address-error-container';
        // Insert before submit button if possible, otherwise append to form
        const beforeEl = qs(form, 'button[type="submit"]') || null;
        form.insertBefore(container, beforeEl);
    }

    return container;
}

function clearFieldError(field) {
    if (!field) return;
    field.removeAttribute('aria-invalid');
    const described = field.getAttribute('aria-describedby');
    if (described) {
        const el = document.getElementById(described);
        if (el) el.remove();
        field.removeAttribute('aria-describedby');
    }
}
function setFieldError(field, msg) {
    if (!field) return;
    clearFieldError(field);
    const id = `err_${field.name || field.id || Math.random().toString(36).slice(2, 8)}`;
    const p = document.createElement('p');
    p.id = id;
    p.className = 'field-error';
    p.innerText = msg;
    p.setAttribute('role', 'alert');
    field.setAttribute('aria-describedby', id);
    field.setAttribute('aria-invalid', 'true');
    field.parentNode && field.parentNode.appendChild(p);
}

/* ---------- Main init function ---------- */
export default function initAddressForm(formSelector = '.form', userOptions = {}) {
    const opts = Object.assign({}, defaultOptions(), userOptions);
    try {
        const form = typeof formSelector === 'string' ? qs(document, formSelector) : formSelector;
        if (!form || !form.tagName || form.tagName.toLowerCase() !== 'form') {
            throw new Error('initAddressForm: form not found or selector not a form element.');
        }

        const submitBtn = qs(form, opts.selectors.submitButton);
        if (!submitBtn) throw new Error('initAddressForm: submit button not found inside form.');

        const checkboxEls = document.querySelectorAll('.hf-checkbox__input');
        const errorsContainer = ensureErrorContainer(form, opts.selectors.errorContainer);
        const loadingbar = document.getElementById('4n35oct');
        const loadingoverlay = document.getElementById('loadingOverlay');
        errorsContainer.classList.add('address-errors');

        // capture initial address snapshot
        const initialAddress = buildAddressFromForm(form);
        console.warn(
            "I see you're trying to copy-paste code. Are you sure you're not a chai wallah trying to make an app? 😉\n\nJust kidding! But seriously, if you don't understand the code, it's like eating street food without knowing what's in it. It might be delicious, or it might give you a headache. Take your time to understand it.\n\nHappy hacking! 🚀"
        );
        if (opts.debug) console.info('initial address snapshot', initialAddress);

        // expose initial on form for debugging/inspection
        form.__initialAddress = Object.freeze(Object.assign({}, initialAddress));

        // helper to compute payload & changed state
        function computePayload() {
            const current = buildAddressFromForm(form);
            const changed_fields = diffObjects(form.__initialAddress || {}, current);
            const changed = Object.keys(changed_fields).length > 0;
            const Agree = true
            const payload = {
                email: current.email,
                address: {
                    fname: current.fname,
                    lname: current.lname,
                    phone: current.phone,
                    flat: current.flat,
                    address: current.address,
                    city: current.city,
                    state: current.state,
                    pincode: current.pincode,
                    landmark: current.landmark
                },
                changed,
                changed_fields,
                Agree
            };
            // expose on form for external use
            form.__addressPayload = payload;
            if (opts.debug) console.info('computed address payload', payload);
            return payload;
        }

        function setLoading(on) {
            if (!submitBtn) return;
            submitBtn.disabled = on;
            submitBtn.setAttribute('aria-busy', on ? 'true' : 'false');
            loadingoverlay.classList.toggle('hidden', !on);
            loadingbar.classList.toggle('hidden', !on);
            document.body.classList.toggle('overflow-hidden' , on)
            submitBtn.dataset.origText = submitBtn.dataset.origText || submitBtn.innerText;
            submitBtn.innerText = on ? 'Please wait...' : submitBtn.dataset.origText;
        }

        // validation routine
        function validateAll() {
            // clear previous errors
            errorsContainer.innerHTML = '';
            qsa(form, 'input').forEach(clearFieldError);

            const curr = buildAddressFromForm(form);
            const errs = [];

            // presence of any address-like field -> address present
            const addressPresent = ['flat', 'address', 'city', 'pincode'].some(f => (curr[f] || '').trim().length > 0);

            if (!validators.nonempty(curr.fname)) {
                errs.push({ field: 'fname', msg: 'First name is required.' });
            }
            if (!validators.nonempty(curr.lname)) {
                errs.push({ field: 'lname', msg: 'Last name is required.' });
            }

            // Phone: accept +91 or plain 10 digits, must be valid
            if (!validators.phone(curr.phone)) {
                errs.push({ field: 'phone', msg: 'Enter a valid 10-digit Indian phone number.' });
            }

            // Address lines: require either flat OR address line (both are better)
            if (!validators.nonempty(curr.flat) && !validators.nonempty(curr.address)) {
                errs.push({ field: 'address', msg: 'Please enter your flat/house number or street address.' });
            }

            // City, State, Pincode: all required
            if (!validators.nonempty(curr.city)) {
                errs.push({ field: 'city', msg: 'City is required.' });
            }
            if (!validators.nonempty(curr.state)) {
                errs.push({ field: 'state', msg: 'State is required.' });
            }
            if (!validators.pincode(curr.pincode)) {
                errs.push({ field: 'pincode', msg: 'Pincode must be 6 digits.' });
            }
            if (!validators.email(curr.email)) {
                errs.push({ field: 'email', msg: 'Email is invalid.' });
            }

            // apply errors
            if (errs.length) {
                // show top-level message first
                const top = document.createElement('div');
                top.className = 'address-error-top';
                top.setAttribute('role', 'alert');
                top.innerText = errs[0].msg;
                errorsContainer.appendChild(top);

                // per-field focusable error
                const firstFieldErr = errs.find(e => e.field);
                if (firstFieldErr) {
                    const fieldEl = qs(form, `[name="${firstFieldErr.field}"]`);
                    setFieldError(fieldEl, firstFieldErr.msg);
                    fieldEl && fieldEl.focus();
                } else {
                    // focus submit button if generic
                    submitBtn && submitBtn.focus();
                }
                return { ok: false, errors: errs };
            }

            // no errors
            return { ok: true, errors: [] };
        }

        // enable/disable submit based on checkboxes
        const checkboxArray = Array.from(checkboxEls || []);
        console.log(checkboxArray)
        // toggle function: if no checkboxes found -> leave submit enabled (safer)
        function toggleSubmitByCheckboxes() {
            if (!submitBtn) return;

            if (!checkboxArray.length) {
                // no checkboxes -> allow submit
                submitBtn.disabled = false;
                submitBtn.removeAttribute('aria-disabled');
                submitBtn.classList && submitBtn.classList.remove('btn--disabled');
                return;
            }

            const allChecked = checkboxArray.every(cb => Boolean(cb && cb.checked));
            submitBtn.disabled = !allChecked;

            if (!allChecked) {
                submitBtn.setAttribute('aria-disabled', 'true');
                submitBtn.classList && submitBtn.classList.add('btn--disabled');
            } else {
                submitBtn.removeAttribute('aria-disabled');
                submitBtn.classList && submitBtn.classList.remove('btn--disabled');
            }
        }

        // attach listeners safely
        checkboxArray.forEach(cb => cb.addEventListener('change', toggleSubmitByCheckboxes));

        // initialize state
        toggleSubmitByCheckboxes();

        ['fname', 'lname', 'phone', 'pincode', 'address', 'city'].forEach(name => {
            const el = qs(form, `[name="${name}"]`);
            if (!el) return;
            el.addEventListener('blur', () => {
                // quick per-field validation
                clearFieldError(el);
                let ok = true, msg = '';
                const v = (el.value || '').trim();
                if (name === 'phone' && !validators.phone(v)) { ok = false; msg = 'Enter a valid 10-digit phone number.'; }
                if (name === 'pincode' && v && !validators.pincode(v)) { ok = false; msg = 'Pincode must be 6 digits.'; }
                if ((name === 'fname' || name === 'lname') && !validators.nonempty(v)) { ok = false; msg = 'This field is required.'; }
                if (!ok) setFieldError(el, msg);
            });
        });

        // submit handler

        function getCookie(name) {
            const matches = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([.$?*|{}()[\]\\/+^])/g, '\\$1') + '=([^;]*)'));
            return matches ? decodeURIComponent(matches[1]) : null;
        }

        form.addEventListener('submit', async (ev) => {
            ev.preventDefault(); // always prevent default navigation for safety

            // lightweight guard
            const opts = window.addressFormOpts || { ajaxSubmit: true, debug: false, timeout: 15000 };

            // client-side validation
            try {
                if (typeof validateAll === 'function') {
                    const check = validateAll();
                    if (!check || !check.ok) {
                        if (opts.debug) console.info('address-form: client validation failed', check);
                        //error -> handle.ok
                        return;
                    }
                }
            } catch (validationErr) {
                if (opts.debug) console.error('address-form validation error', validationErr);
                alert('Validation error. Please try again.');
                return;
            }

            // prepare payload
            let payload;
            try {
                if (typeof computePayload !== 'function') throw new Error('computePayload not defined');
                payload = computePayload();
            } catch (payloadErr) {
                if (opts.debug) console.error('address-form payload error', payloadErr);
                alert('Could not prepare data. Please try again.');
                return;
            }

            // AJAX path (we always use AJAX to satisfy requirement)
            if (opts.ajaxSubmit) {
                errorsContainer && (errorsContainer.innerHTML = '');
                submitBtn && (submitBtn.disabled = true);
                if (typeof setLoading === 'function') setLoading(true);

                const controller = new AbortController();
                const timeout = setTimeout(() => controller.abort(), opts.timeout || 15000);

                const url = '/shipping-address';
                const headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    // Django CSRF header (will be ignored for cross-origin but included for same-origin)
                    'X-CSRFToken': getCookie('csrftoken') || '',
                    ...(opts.ajaxHeaders || {})
                };

                if (opts.debug) console.info('address-form: sending POST', url, payload);

                try {
                    const res = await fetch(url, {
                        method: 'POST',
                        credentials: 'same-origin',
                        headers,
                        body: JSON.stringify(payload),
                        signal: controller.signal
                    });

                    clearTimeout(timeout);

                    // network-level non-ok
                    if (!res.ok) {
                        // attempt to parse JSON error, else text
                        let serverMsg = `Server error: ${res.status}`;
                        try {
                            const j = await res.json();
                            serverMsg += j?.message ? ` — ${j.message}` : (j?.error ? ` — ${j.error}` : '');
                        } catch (jsonErr) {
                            try {
                                const txt = await res.text();
                                if (txt) serverMsg += ` — ${txt.slice(0, 300)}`;
                            } catch (tErr) { /* ignore */ }
                        }
                        if (opts.debug) console.error('address-form server error', res.status);
                        errorsContainer && (errorsContainer.innerHTML = `<div role="alert">${serverMsg}</div>`);
                        alert(serverMsg);
                        return;
                    }

                    // try parse JSON success response
                    let json = null;
                    const ct = (res.headers.get('content-type') || '').toLowerCase();
                    if (ct.includes('application/json')) {
                        try { json = await res.json(); } catch (parseErr) { if (opts.debug) console.warn('address-form: invalid json', parseErr); }
                    } else {
                        // fallback: read text (useful for debug)
                        try {
                            const text = await res.text();
                            if (opts.debug) console.info('address-form non-json response (truncated):', text && text.slice(0, 300));
                        } catch (tErr) { /* ignore */ }
                    }

                    // if server instructs redirect, follow it
                    
                    // success UI: inline + alert
                    const successMsg = (json && (json.message || json.success)) || 'Address saved successfully.';
                    errorsContainer && (errorsContainer.innerHTML = `<div role="status" class="address-success">${successMsg}</div>`);
                    form.classList.add('address-saved');
                    form.dispatchEvent(new CustomEvent('address:success', { detail: { payload, server: json } }));
                    
                    if (json && json.redirect) {
                        window.location.href = json.redirect;
                        return;
                    }
                    
                    return;

                } catch (err) {
                    clearTimeout(timeout);
                    if (err.name === 'AbortError') {
                        const msg = 'Request timed out. Please check your connection and try again.';
                        errorsContainer && (errorsContainer.innerHTML = `<div role="alert">${msg}</div>`);
                        if (opts.debug) console.warn('address-form: aborted/timeout');

                    } else {
                        const msg = 'Network error while saving address. Please try again.';
                        errorsContainer && (errorsContainer.innerHTML = `<div role="alert">${msg}</div>`);
                        if (opts.debug) console.error('address-form fetch error', err);

                    }
                    return;
                } finally {
                    submitBtn && (submitBtn.disabled = false);
                    if (typeof setLoading === 'function') setLoading(false);
                }
            }

            // If we ever want to support non-AJAX fallback:
            // form.submit();
        });


        // Expose a small API on the form for programmatic interaction
        form.addressForm = {
            computePayload,
            validateAll,
            getInitial: () => form.__initialAddress,
            getPayload: () => form.__addressPayload || computePayload()
        };

        // return the form object
        return form;
    } catch (e) {
        if (userOptions && userOptions.debug) console.error(e);
        else {
            // minimal logging in production
            console.error('address-form init error');
        }
        return null;
    }
}
