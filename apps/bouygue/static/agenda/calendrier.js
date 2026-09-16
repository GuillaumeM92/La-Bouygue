/* The stays calendar.
 *
 * Two views of the same stays: the FullCalendar month grid, and a list of the
 * stays to come (the default on phones). Both open one window
 * (blocks/sejour-fenetre.html) that shows a stay, edits it or deletes it.
 * Stays come from /reservations/; the form posts to /agenda/ and deletion
 * goes through /delete_reservation/.
 */
document.addEventListener('DOMContentLoaded', function () {
    const config = JSON.parse(document.getElementById('agenda-config').textContent);
    const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    const csrftoken = cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
    const calendarEl = document.getElementById('calendar');
    const upcomingEl = document.getElementById('upcoming-stays');
    const phone = window.matchMedia('(max-width: 767.98px)').matches;
    const mouse = window.matchMedia('(hover: hover)').matches;
    let stays = [];
    let calendar = null;

    /* ------------------------------------------------------------------ */
    /* Dates                                                               */
    /* ------------------------------------------------------------------ */

    const toDate = function (iso) {
        const parts = iso.split('-');
        return new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    };
    const toIso = function (date) {
        const pad = n => String(n).padStart(2, '0');
        return date.getFullYear() + '-' + pad(date.getMonth() + 1) + '-' + pad(date.getDate());
    };
    const addDays = function (iso, days) {
        const date = toDate(iso);
        date.setDate(date.getDate() + days);
        return toIso(date);
    };
    const nights = function (start, end) {
        return Math.round((toDate(end) - toDate(start)) / 86400000);
    };
    const nightsLabel = function (start, end) {
        const n = nights(start, end);
        if (n < 0) { return ''; }
        if (n === 0) { return 'dans la journée'; }
        return n + (n > 1 ? ' nuits' : ' nuit');
    };

    // "du lun. 6 au ven. 10 oct.", with the year only when it is not this one
    const stayDates = function (startIso, endIso) {
        const start = toDate(startIso);
        const end = toDate(endIso);
        const thisYear = new Date().getFullYear();
        if (startIso === endIso) {
            return 'le ' + start.toLocaleDateString('fr-FR', Object.assign(
                { weekday: 'short', day: 'numeric', month: 'short' },
                start.getFullYear() === thisYear ? {} : { year: 'numeric' }));
        }
        const sameYear = start.getFullYear() === end.getFullYear();
        const sameMonth = sameYear && start.getMonth() === end.getMonth();
        const withYear = sameYear && start.getFullYear() === thisYear ? {} : { year: 'numeric' };
        const from = start.toLocaleDateString('fr-FR', Object.assign(
            { weekday: 'short', day: 'numeric' }, sameMonth ? {} : { month: 'short' }, sameYear ? {} : withYear));
        const to = end.toLocaleDateString('fr-FR', Object.assign(
            { weekday: 'short', day: 'numeric', month: 'short' }, withYear));
        return 'du ' + from + ' au ' + to;
    };

    // Same rule as the server: stays clash when they share a night; a
    // departure and an arrival on the same day do not.
    const occupied = function (start, end) {
        return [start, end > start ? end : addDays(start, 1)];
    };
    const clashes = function (start, end, exceptId) {
        const mine = occupied(start, end);
        return stays.filter(function (stay) {
            if (stay.id === exceptId) { return false; }
            const theirs = occupied(stay.start_date, stay.end_date);
            return theirs[0] < mine[1] && mine[0] < theirs[1];
        });
    };

    /* ------------------------------------------------------------------ */
    /* One colour per person                                               */
    /* ------------------------------------------------------------------ */

    // The colour comes with each stay (agenda/models.py, STAY_COLORS)
    const canChange = stay => config.isAdmin || stay.user_id === config.userId;
    const ownerOf = stay => ((stay.owner_surname || '') + ' ' + (stay.owner_name || '')).trim() || 'un membre';

    /* ------------------------------------------------------------------ */
    /* The stay window                                                     */
    /* ------------------------------------------------------------------ */

    const modal = $('#sejour-fenetre');
    const title = document.getElementById('sejour-titre');
    const form = modal.find('form[data-temps="saisir"]')[0];
    const field = name => form.elements[name];
    const durationEl = document.getElementById('sejour-duree');
    const clashEl = document.getElementById('sejour-chevauchement');
    let current = null; // the stay being shown, edited or deleted

    const show = function (temps) {
        modal.find('[data-temps]').each(function () { this.hidden = this.dataset.temps !== temps; });
        if (!modal.hasClass('show')) { modal.modal('show'); }
    };
    const fill = function (temps, stay) {
        const part = modal.find('[data-temps="' + temps + '"]');
        part.find('[data-champ="nom"]').text(stay.name);
        part.find('[data-champ="dates"]').text(stayDates(stay.start_date, stay.end_date));
        part.find('[data-champ="nuits"]').text('(' + nightsLabel(stay.start_date, stay.end_date) + ')');
        part.find('[data-champ="auteur"]').text(stay.user_id === config.userId ? 'vous' : ownerOf(stay));
        part.find('[data-champ="description"]').text(stay.description || '').prop('hidden', !stay.description);
        part.find('.berg-sejour-couleur').css('background-color', stay.color);
    };

    const consult = function (stay) {
        current = stay;
        title.textContent = 'Le séjour';
        fill('consulter', stay);
        modal.find('[data-action="modifier"], [data-action="demander-suppression"]').prop('hidden', !canChange(stay));
        modal.find('[data-action="proposer-echange"]').prop('hidden', !canAskExchange(stay));
        modal.find('[data-action="ecrire"]').prop('hidden', stay.user_id === config.userId);
        show('consulter');
    };

    // An exchange: someone else's stay still to come, for one of mine still to come
    const myComingStays = () => stays.filter(s => s.user_id === config.userId && s.end_date >= toIso(new Date()));
    const canAskExchange = stay => stay.user_id !== config.userId && stay.end_date >= toIso(new Date())
        && myComingStays().length > 0;
    const exchangeForm = modal.find('form[data-temps="echanger"]')[0];
    const askExchange = function (stay) {
        title.textContent = 'Demander un échange';
        fill('echanger', stay);
        exchangeForm.elements.requested.value = stay.id;
        const select = exchangeForm.elements.offered;
        select.textContent = '';
        myComingStays().forEach(function (mine) {
            const option = document.createElement('option');
            option.value = mine.id;
            option.textContent = mine.name + ' — ' + stayDates(mine.start_date, mine.end_date);
            select.appendChild(option);
        });
        show('echanger');
    };

    const clearErrors = function () {
        $(form).find('.is-invalid').removeClass('is-invalid');
        $(form).find('.invalid-feedback, .alert-block').remove();
    };

    const refreshHints = function () {
        const start = field('start_date').value;
        const end = field('end_date').value;
        field('end_date').min = start;
        durationEl.textContent = start && end && end >= start
            ? stayDates(start, end) + ' — ' + nightsLabel(start, end) : '';
        const others = start && end && end >= start ? clashes(start, end, current ? current.id : null) : [];
        clashEl.hidden = !others.length;
        clashEl.textContent = others.length
            ? 'En même temps que : ' + others.map(o => o.name + ' (' + stayDates(o.start_date, o.end_date) + ')').join(' ; ')
              + '. Vous pouvez enregistrer quand même : pensez à vous coordonner.'
            : '';
    };

    const edit = function (stay, start, end) {
        current = stay;
        clearErrors();
        title.textContent = stay ? 'Modifier le séjour' : 'Poser un séjour';
        field('id').value = stay ? stay.id : '';
        field('name').value = stay ? stay.name : config.defaultName;
        field('start_date').value = stay ? stay.start_date : (start || '');
        field('end_date').value = stay ? stay.end_date : (end || '');
        field('description').value = stay ? stay.description : '';
        refreshHints();
        show('saisir');
        // Focus the first thing left to fill in
        setTimeout(function () {
            const next = !field('start_date').value ? field('start_date') : field('name');
            if (!phone) { next.focus(); }
        }, 400);
    };

    field('start_date').addEventListener('change', function () {
        const end = field('end_date');
        if (this.value && (!end.value || end.value < this.value)) { end.value = this.value; }
        refreshHints();
    });
    field('end_date').addEventListener('change', refreshHints);

    modal.on('click', '[data-action]', function () {
        const action = this.dataset.action;
        if (action === 'modifier') { edit(current); }
        if (action === 'consulter') { consult(current); }
        if (action === 'proposer-echange') { askExchange(current); }
        if (action === 'ecrire') {
            title.textContent = 'Écrire à ' + ownerOf(current);
            fill('ecrire', current);
            const writeForm = modal.find('form[data-temps="ecrire"]')[0];
            writeForm.action = '/reservation/' + current.id + '/ecrire/';
            show('ecrire');
            if (!phone) { setTimeout(() => writeForm.elements.message.focus(), 300); }
        }
        if (action === 'demander-suppression') {
            title.textContent = 'Supprimer le séjour';
            fill('supprimer', current);
            show('supprimer');
        }
        if (action === 'supprimer') {
            this.disabled = true;
            fetch('/delete_reservation/', {
                method: 'DELETE',
                body: JSON.stringify({ id: current.id }),
                headers: { 'X-CSRFToken': csrftoken }
            }).finally(function () {
                // The page shows the server's message and the updated calendar
                window.location.href = '/agenda/';
            });
        }
    });
    document.querySelector('[data-action="nouveau"]').addEventListener('click', function () { edit(null); });

    /* ------------------------------------------------------------------ */
    /* The month grid                                                      */
    /* ------------------------------------------------------------------ */

    const buildCalendar = function () {
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'fr',
            firstDay: 1,
            expandRows: true,
            headerToolbar: phone
                ? { left: 'prev', center: 'title', right: 'next' }
                : { left: 'prev,next today', center: 'title', right: 'dayGridMonth,listMonth' },
            buttonText: { today: 'Aujourd\'hui', month: 'Mois', list: 'Liste' },
            aspectRatio: phone ? 0.8 : 1.35,
            dayMaxEvents: true,
            // Drag across days (or hold, on a touch screen) to pose a stay
            selectable: true,
            selectLongPressDelay: 350,
            select: function (info) {
                edit(null, info.startStr, addDays(info.endStr, -1));
                calendar.unselect();
            },
            events: stays.map(stay => ({
                id: String(stay.id),
                title: stay.name,
                start: stay.start_date,
                // FullCalendar's all-day end is the day after the last one
                end: addDays(stay.end_date, 1),
                allDay: true,
                backgroundColor: stay.color,
                borderColor: stay.color,
                extendedProps: { stay: stay },
            })),
            eventClick: function (info) { consult(info.event.extendedProps.stay); },
            // Show the description under the stay's name while the pointer is on it
            eventMouseEnter: function (info) {
                const description = info.event.extendedProps.stay.description;
                if (!mouse || !description || !info.view.type.startsWith('dayGrid') ||
                    info.el.querySelector('.berg-fc-description')) { return; }
                const line = document.createElement('span');
                line.className = 'berg-fc-description';
                line.textContent = description;
                info.el.appendChild(line);
            },
            eventMouseLeave: function (info) {
                const line = info.el.querySelector('.berg-fc-description');
                if (line) { line.remove(); }
            },
        });
        calendar.render();
    };

    /* ------------------------------------------------------------------ */
    /* The list of stays to come                                           */
    /* ------------------------------------------------------------------ */

    const element = function (tag, className, text) {
        const node = document.createElement(tag);
        if (className) { node.className = className; }
        if (text) { node.textContent = text; }
        return node;
    };

    const buildUpcoming = function () {
        const today = toIso(new Date());
        const coming = stays.filter(stay => stay.end_date >= today);
        upcomingEl.textContent = '';
        if (!coming.length) {
            upcomingEl.appendChild(element('p', 'berg-vide', 'Aucun séjour prévu pour l\'instant.'));
            return;
        }
        let month = null;
        let list = null;
        coming.forEach(function (stay) {
            const label = stay.start_date <= today
                ? 'En ce moment'
                : toDate(stay.start_date).toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
            if (label !== month) {
                month = label;
                upcomingEl.appendChild(element('h2', 'berg-sejours-mois', label));
                list = upcomingEl.appendChild(element('ul', 'berg-sejours'));
            }
            const card = element('button', 'berg-sejour');
            card.type = 'button';
            card.style.borderLeftColor = stay.color;
            card.appendChild(element('span', 'berg-sejour-nom', stay.name));
            card.appendChild(element('span', 'berg-sejour-dates',
                stayDates(stay.start_date, stay.end_date) + ' · ' + nightsLabel(stay.start_date, stay.end_date)));
            if (stay.description) {
                card.appendChild(element('span', 'berg-sejour-desc', stay.description));
            }
            card.appendChild(element('span', 'berg-sejour-auteur',
                stay.user_id === config.userId ? 'Votre séjour' : 'Posé par ' + ownerOf(stay)));
            card.addEventListener('click', function () { consult(stay); });
            list.appendChild(element('li')).appendChild(card);
        });
    };

    /* ------------------------------------------------------------------ */
    /* Switching between the two views                                     */
    /* ------------------------------------------------------------------ */

    const tabs = $('.berg-agenda-vues [data-vue]');
    const showView = function (view) {
        tabs.each(function () {
            const active = this.dataset.vue === view;
            this.classList.toggle('active', active);
            this.setAttribute('aria-selected', active ? 'true' : 'false');
        });
        upcomingEl.hidden = view !== 'liste';
        calendarEl.hidden = view !== 'calendrier';
        if (view === 'calendrier') {
            // FullCalendar measures its container: build it once it is visible
            if (calendar) { calendar.updateSize(); } else { buildCalendar(); }
        }
        try { localStorage.setItem('agenda-vue', view); } catch (e) { /* private mode */ }
    };
    tabs.on('click', function () { showView(this.dataset.vue); });

    fetch('/reservations/')
        .then(response => response.json())
        .then(function (data) {
            stays = data;
            buildUpcoming();
            let view = phone ? 'liste' : 'calendrier';
            try {
                const saved = localStorage.getItem('agenda-vue');
                if (saved === 'liste' || saved === 'calendrier') { view = saved; }
            } catch (e) { /* private mode */ }
            showView(view);

            // A refused form comes back with its errors: open it again as it was
            if (config.reopen) {
                current = stays.find(stay => String(stay.id) === String(config.reopen)) || null;
                title.textContent = current ? 'Modifier le séjour' : 'Poser un séjour';
                refreshHints();
                show('saisir');
            }
        });
});
