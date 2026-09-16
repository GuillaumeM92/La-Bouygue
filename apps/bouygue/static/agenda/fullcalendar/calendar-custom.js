/* The stays calendar.
 *
 * Two views of the same stays: the FullCalendar month grid, and a list of the
 * stays to come, which is the default on phones. Both open the same modals.
 * The server side is unchanged: stays are read from /reservations/ and
 * /reservation/, deleted through /delete_reservation/, and the forms still post
 * their dates as dd/mm/yyyy.
 */
document.addEventListener('DOMContentLoaded', function () {
    const csrftoken = Cookies.get('csrftoken')
    const user_id = $("#user_id").attr("value")
    const is_admin = $("#is_admin").attr("value")
    const calendarEl = document.getElementById('calendar');
    const upcomingEl = document.getElementById('upcoming-stays');
    const phone = window.matchMedia('(max-width: 767.98px)').matches;
    // Phones and tablets get the operating system's date picker
    const nativeDates = window.matchMedia('(max-width: 767.98px), (pointer: coarse)').matches;
    const mouse = window.matchMedia('(hover: hover)').matches;
    let reservationsDict = []; // create an empty array
    let calendar = null;
    // The stay shown in the 'modify reservation' modal, the one a delete targets
    let openReservationID = null;

    // Stays were saved with a random shade of blue; show them in the site's colours
    const palette = ['#ae5029', '#3e5540', '#8a5a38', '#9d3626', '#56704f', '#7a4f2a', '#4b5a4e'];
    const stayColor = function (id) { return palette[id % palette.length]; };

    /* ------------------------------------------------------------------ */
    /* Dates                                                               */
    /* ------------------------------------------------------------------ */

    // '2026-09-09' <-> '09/09/2026' (the format the server expects)
    const isoToFrench = function (iso) {
        const parts = (iso || '').split('-');
        return parts.length === 3 ? parts[2] + '/' + parts[1] + '/' + parts[0] : '';
    };
    const frenchToIso = function (french) {
        const parts = (french || '').split('/');
        return parts.length === 3 ? parts[2] + '-' + parts[1] + '-' + parts[0] : '';
    };
    const isoToDate = function (iso) {
        const parts = iso.split('-');
        return new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    };

    // Each date field of the two forms, in page order: the admin date widget
    // numbers its calendars (#calendarbox0 to #calendarbox3) the same way.
    const dateFields = $('input.vDateField').toArray();

    if (nativeDates) {
        document.body.classList.add('berg-dates-natives');
        dateFields.forEach(function (field) {
            // A native date input stands in for the text field, which stays in
            // the form, hidden, and keeps carrying the dd/mm/yyyy value.
            const native = document.createElement('input');
            native.type = 'date';
            native.className = field.className.replace('vDateField', '') + ' berg-date';
            native.id = field.id;
            native.required = field.required;
            native.value = frenchToIso(field.value);
            field.removeAttribute('id');
            field.required = false;
            field.hidden = true;
            field.parentNode.insertBefore(native, field);
            field.nativeInput = native;
            native.addEventListener('change', function () {
                field.value = isoToFrench(native.value);
                if (field.name === 'start_date') {
                    const end = $(field.form).find('input[name=end_date]')[0];
                    end.nativeInput.min = native.value;
                    if (end.nativeInput.value && end.nativeInput.value < native.value) {
                        end.nativeInput.value = native.value;
                        end.value = field.value;
                    }
                }
            });
        });
    }

    const setDate = function (form, name, french) {
        const field = form.find('input[name=' + name + ']')[0];
        field.value = french;
        if (field.nativeInput) {
            field.nativeInput.value = frenchToIso(french);
            if (name === 'end_date') {
                field.nativeInput.min = form.find('input[name=start_date]')[0].nativeInput.value;
            }
        }
    };

    /* ------------------------------------------------------------------ */
    /* Opening, editing and deleting a stay                                */
    /* ------------------------------------------------------------------ */

    const openReservation = function (reservationID, ownerID) {
        fetch("/reservation/", {
            method: "POST",
            body: JSON.stringify({ id: reservationID }),
            headers: { "X-CSRFToken": csrftoken }
        })
            .then(response => response.json())
            .then(function (data) {
                const fields = JSON.parse(data)[0]["fields"]
                const startDate = isoToFrench(fields["start_date"])
                const endDate = isoToFrench(fields["end_date"])
                // check if the user is the owner of the reservation
                if (user_id == ownerID || is_admin == "yes") {
                    openReservationID = reservationID
                    // Insert the reservation data in the 'modify reservation' modal
                    const modifyForm = $("#staticBackdrop2 form")
                    modifyForm.find("input[name=id]").val(reservationID)
                    modifyForm.find("input[name=name]").val(fields["name"])
                    setDate(modifyForm, "start_date", startDate)
                    setDate(modifyForm, "end_date", endDate)
                    modifyForm.find("textarea[name=description]").val(fields["description"])
                    $('#modify-reservation-button').click()
                } else {
                    // Insert the reservation data in the 'view reservation' modal
                    const viewModal = $("#staticBackdrop3")
                    viewModal.find("#view_name").text(fields["name"])
                    viewModal.find("#view_start_date").text(startDate)
                    viewModal.find("#view_end_date").text(endDate)
                    viewModal.find("#view_description").text(fields["description"])
                    $('#view-reservation-button').click()
                }
            });
    };

    // Bound once: it deletes the stay currently open in the 'modify' modal,
    // and nothing else.
    $("#delete-reservation").on("click", function () {
        if (!openReservationID) { return; }
        this.disabled = true;
        fetch("/delete_reservation/", {
            method: "DELETE",
            body: JSON.stringify({ id: openReservationID }),
            headers: { "X-CSRFToken": csrftoken }
        })
            .finally(function () {
                // Reload the page to update the calendar and show the message
                window.location.href = "/agenda/";
            });
    });

    /* ------------------------------------------------------------------ */
    /* The month grid                                                      */
    /* ------------------------------------------------------------------ */

    const buildCalendar = function () {
        calendar = new FullCalendar.Calendar(calendarEl, {
            expandRows: true,
            initialView: 'dayGridMonth',
            firstDay: 1,
            displayEventTime: false,
            headerToolbar: phone
                ? { left: 'prev', center: 'title', right: 'next' }
                : {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,dayGridWeek,dayGridDay,listWeek'
                },
            // Taller than wide on a phone, so each week keeps some room
            aspectRatio: phone ? 0.8 : 1.35,
            locale: 'fr',
            buttonText: {
                today: 'Aujourd\'hui',
                month: 'Mois',
                week: 'Semaine',
                day: 'Jour',
                list: 'Liste',
            },
            navLinks: !phone, // can click day/week names to navigate views
            editable: false,
            selectable: true,
            nowIndicator: true,
            dayMaxEvents: true, // allow "more" link when too many events
            events: reservationsDict,
            eventClick: function (clickInfo) {
                const props = clickInfo.event.extendedProps
                openReservation(props.reservationID, props.userID)
            },
            // Show the description under the stay's name while the pointer is on it
            eventMouseEnter: function (info) {
                const description = info.event.extendedProps.description;
                if (!mouse || !description || !info.view.type.startsWith('dayGrid') ||
                    info.el.querySelector('.berg-fc-description')) { return; }
                const line = document.createElement('span');
                line.className = 'berg-fc-description';
                line.textContent = 'Description : ' + description;
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

    const stayDates = function (start, end) {
        const thisYearOnly = start.getFullYear() === new Date().getFullYear() ? {} : { year: 'numeric' };
        if (start.getTime() === end.getTime()) {
            return 'le ' + start.toLocaleDateString('fr-FR', Object.assign(
                { weekday: 'short', day: 'numeric', month: 'short' }, thisYearOnly));
        }
        const sameYear = start.getFullYear() === end.getFullYear();
        const sameMonth = sameYear && start.getMonth() === end.getMonth();
        const thisYear = sameYear && start.getFullYear() === new Date().getFullYear();
        const withYear = thisYear ? {} : { year: 'numeric' };
        const from = start.toLocaleDateString('fr-FR', Object.assign(
            { weekday: 'short', day: 'numeric' }, sameMonth ? {} : { month: 'short' }, sameYear ? {} : withYear));
        const to = end.toLocaleDateString('fr-FR', Object.assign(
            { weekday: 'short', day: 'numeric', month: 'short' }, withYear));
        return 'du ' + from + ' au ' + to;
    };

    const buildUpcoming = function () {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const stays = reservationsDict
            .filter(stay => isoToDate(stay.end_date) >= today)
            .sort((a, b) => a.start_date.localeCompare(b.start_date) || a.end_date.localeCompare(b.end_date));

        upcomingEl.textContent = '';
        if (!stays.length) {
            upcomingEl.appendChild(element('p', 'berg-vide', 'Aucun séjour prévu pour l\'instant.'));
            return;
        }
        let month = null;
        let list = null;
        stays.forEach(function (stay) {
            const start = isoToDate(stay.start_date);
            const end = isoToDate(stay.end_date);
            const label = start <= today
                ? 'En ce moment'
                : start.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
            if (label !== month) {
                month = label;
                upcomingEl.appendChild(element('h2', 'berg-sejours-mois', label));
                list = upcomingEl.appendChild(element('ul', 'berg-sejours'));
            }
            const card = element('button', 'berg-sejour');
            card.type = 'button';
            card.style.borderLeftColor = stay.backgroundColor;
            card.appendChild(element('span', 'berg-sejour-nom', stay.title));
            card.appendChild(element('span', 'berg-sejour-dates', stayDates(start, end)));
            if (stay.description) {
                card.appendChild(element('span', 'berg-sejour-desc', stay.description));
            }
            if (user_id == stay.userID) {
                card.appendChild(element('span', 'berg-sejour-marque', 'Votre séjour'));
            }
            card.addEventListener('click', function () {
                openReservation(stay.reservationID, stay.userID);
            });
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
            // Fill the calendar with reservations from the DB(through json url)
            for (const reservation of data) {
                reservationsDict.push({
                    title: reservation["name"],
                    start: reservation["start_date"] + 'T12:00:00',
                    end: reservation["end_date"] + 'T12:00:00',
                    backgroundColor: stayColor(reservation["id"]),
                    reservationID: reservation["id"],
                    userID: reservation["user_id"],
                    description: reservation["description"],
                    start_date: reservation["start_date"],
                    end_date: reservation["end_date"],
                });
            }
            buildUpcoming();
            let view = phone ? 'liste' : 'calendrier';
            try {
                const saved = localStorage.getItem('agenda-vue');
                if (saved === 'liste' || saved === 'calendrier') { view = saved; }
            } catch (e) { /* private mode */ }
            showView(view);
        });

    /* ------------------------------------------------------------------ */
    /* The admin date widget (computers only)                              */
    /* ------------------------------------------------------------------ */

    //Make sure the calendar widget displays on top of the form modal window
    $(window).on('load', function () {
        let datePicker = document.getElementsByClassName('calendarbox module');
        let modalWindow = document.getElementById("staticBackdrop")
        let modalWindow2 = document.getElementById("staticBackdrop2")
        modalWindow.appendChild(datePicker[0])
        modalWindow.appendChild(datePicker[1])
        modalWindow2.appendChild(datePicker[2])
        modalWindow2.appendChild(datePicker[3])
    });

    const closeDatePickers = function (except) {
        dateFields.forEach(function (field, index) {
            const box = document.getElementById('calendarbox' + index);
            if (box && index !== except) { box.style.display = 'none'; }
        });
    };

    /* Open the widget under the date field that was clicked, and close any
       other one: a click inside a widget never reaches this handler. */
    $(window).on("click", function (e) {
        const index = dateFields.indexOf(e.target);
        closeDatePickers(index);
        if (index === -1 || nativeDates) { return; }
        const box = document.getElementById('calendarbox' + index);
        const modal = e.target.closest('.modal');
        const field = e.target.getBoundingClientRect();
        // Below the "Today | calendar" links the widget adds under the field
        const links = e.target.nextElementSibling || e.target;
        $(e.target).attr("inputmode", "none")
        box.style.display = 'block';
        box.style.left = field.left + 'px';
        box.style.top = (links.getBoundingClientRect().bottom + modal.scrollTop + 4) + 'px';
    });
    $('.modal').on('hidden.bs.modal', function (e) {
        if (e.target === this) { closeDatePickers(-1); }
    });
});
