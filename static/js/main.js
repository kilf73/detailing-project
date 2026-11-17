document.addEventListener('DOMContentLoaded', () => {
    const burgerBtn = document.getElementById('burgerBtn');
    const mainNav = document.getElementById('mainNav');
    if (burgerBtn && mainNav) {
        burgerBtn.addEventListener('click', () => {
            const expanded = burgerBtn.getAttribute('aria-expanded') === 'true';
            burgerBtn.setAttribute('aria-expanded', String(!expanded));
            mainNav.classList.toggle('is-open');
        });
    }

    const bodyBtns = document.querySelectorAll('.js-body-calc');
    const calcResult = document.getElementById('calcResultBar');
    if (bodyBtns.length && calcResult) {
        bodyBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                bodyBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const coeff = parseFloat(btn.dataset.coeff || '1');
                const wash = Math.round(1500 * coeff).toLocaleString('ru-RU');
                const polish = Math.round(12000 * coeff).toLocaleString('ru-RU');
                calcResult.textContent = `Комплексная мойка: ${wash} руб. | Полировка: ${polish} руб.`;
            });
        });
    }

    const searchInput = document.getElementById('liveSearchInput');
    const bodySelect = document.getElementById('liveBodySelect');
    const catBtns = document.querySelectorAll('.js-cat-filter');
    const servicesContainer = document.getElementById('servicesListContainer');
    const loader = document.getElementById('fetchLoader');
    let activeCategory = '';

    async function loadFilteredServices() {
        if (!servicesContainer) return;
        const q = searchInput ? searchInput.value.trim() : '';
        const bodyType = bodySelect ? bodySelect.value : '';
        if (loader) loader.hidden = false;

        try {
            const params = new URLSearchParams({ category: activeCategory, q, body_type: bodyType });
            const resp = await fetch(`/api/services/?${params.toString()}`);
            if (!resp.ok) throw new Error('Ошибка сети');
            const data = await resp.json();

            if (!data.items.length) {
                servicesContainer.innerHTML = '<p class="empty-msg">Услуги по заданным параметрам не найдены.</p>';
            } else {
                servicesContainer.innerHTML = data.items.map(item => `
                    <article class="service-row-card">
                        <div class="service-info-left">
                            <h3><a href="/services/${item.id}/">${item.name}</a></h3>
                            <p>Категория: ${item.category}</p>
                            <div class="service-meta">${item.duration} мин. | ${item.price.toLocaleString('ru-RU')} руб.</div>
                        </div>
                        <a href="/booking/?service=${item.id}" class="btn-action-sm">Записаться</a>
                    </article>
                `).join('');
            }
        } catch (err) {
            console.error(err);
        } finally {
            if (loader) loader.hidden = true;
        }
    }

    if (searchInput) {
        let timer;
        searchInput.addEventListener('input', () => {
            clearTimeout(timer);
            timer = setTimeout(loadFilteredServices, 250);
        });
    }
    if (bodySelect) bodySelect.addEventListener('change', loadFilteredServices);
    catBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            catBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeCategory = btn.dataset.slug || '';
            loadFilteredServices();
        });
    });

    const boxSelect = document.getElementById('id_box');
    const dateInput = document.getElementById('id_booking_date');
    const timeInput = document.getElementById('id_start_time');
    const slotsWrap = document.getElementById('dynamicSlotsGrid');

    async function refreshSlots() {
        if (!boxSelect || !dateInput || !slotsWrap) return;
        const url = `/api/box-slots/?box_id=${encodeURIComponent(boxSelect.value)}&date=${encodeURIComponent(dateInput.value)}`;
        try {
            const resp = await fetch(url);
            const data = await resp.json();
            slotsWrap.innerHTML = data.slots.map(s => `
                <button type="button"
                    class="time-slot-btn ${s.is_free ? 'free' : 'busy'}"
                    ${s.is_free ? '' : 'disabled'}
                    data-time="${s.time}">
                    ${s.time} ${s.is_free ? '' : '(занято)'}
                </button>
            `).join('');

            slotsWrap.querySelectorAll('.time-slot-btn.free').forEach(btn => {
                btn.addEventListener('click', () => {
                    if (timeInput) timeInput.value = btn.dataset.time;
                    slotsWrap.querySelectorAll('.time-slot-btn').forEach(b => b.classList.remove('selected'));
                    btn.classList.add('selected');
                });
            });
        } catch (e) {
            console.error(e);
        }
    }

    if (boxSelect && dateInput) {
        boxSelect.addEventListener('change', refreshSlots);
        dateInput.addEventListener('change', refreshSlots);
        refreshSlots();
    }

    document.querySelectorAll('form.js-validate-form').forEach(form => {
        form.addEventListener('submit', e => {
            let hasError = false;
            form.querySelectorAll('.client-field-error').forEach(el => el.remove());

            form.querySelectorAll('[required]').forEach(field => {
                if (!field.value.trim()) {
                    showFieldError(field, 'Это поле обязательно для заполнения.');
                    hasError = true;
                }
            });

            const phoneField = form.querySelector('[data-validate="phone"]');
            if (phoneField && phoneField.value.trim()) {
                const digits = phoneField.value.replace(/\D/g, '');
                if (digits.length < 10 || digits.length > 15) {
                    showFieldError(phoneField, 'Введите корректный телефон (10–15 цифр).');
                    hasError = true;
                }
            }

            const maxField = form.querySelector('[data-maxlength]');
            if (maxField) {
                const limit = parseInt(maxField.dataset.maxlength, 10);
                if (maxField.value.length > limit) {
                    showFieldError(maxField, `Превышена максимальная длина (${limit} символов).`);
                    hasError = true;
                }
            }

            if (hasError) e.preventDefault();
        });
    });

    function showFieldError(input, msg) {
        const err = document.createElement('div');
        err.className = 'field-error client-field-error';
        err.textContent = msg;
        input.insertAdjacentElement('afterend', err);
    }
});
