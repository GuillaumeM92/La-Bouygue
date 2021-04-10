document.addEventListener('DOMContentLoaded', function () {
    let calendarEl = document.getElementById('calendar');
    let xmlhttp = new XMLHttpRequest()
    let url = "/reservations/"

    const csrftoken = Cookies.get('csrftoken')
    const user_id = $("#user_id").attr("value")
    const is_admin = $("#is_admin").attr("value")

    // these HTTP methods do not require CSRF protection
    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    // setting the csrf token for ajax post request
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Full calendar async handling
    xmlhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let reservations = JSON.parse(xmlhttp.responseText)
            let reservationsDict = []; // create an empty array

            // Fill the calendar with reservations from the DB(through json url)
            for (const reservation of reservations) {
                reservationsDict.push({
                    title: reservation["name"],
                    start: reservation["start_date"] + 'T12:00:00',
                    end: reservation["end_date"] + 'T12:00:00',
                    backgroundColor: reservation["color"],
                    reservationID: reservation["id"],
                    userID: reservation["user_id"],
                    description: reservation["description"],
                    start_date: reservation["start_date"],
                    end_date: reservation["end_date"],
                });
            }

            // Full calendar settings
            let calendar = new FullCalendar.Calendar(calendarEl, {
                expandRows: true,
                initialView: 'dayGridMonth',
                firstDay: 1,
                displayEventTime: false,

                headerToolbar: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,dayGridWeek,dayGridDay,listWeek'
                },
                locale: 'fr',
                buttonText: {
                    today: 'Aujourd\'hui',
                    month: 'Mois',
                    week: 'Semaine',
                    day: 'Jour',
                    list: 'Liste',
                },
                navLinks: true, // can click day/week names to navigate views
                editable: false,
                selectable: true,
                nowIndicator: true,
                dayMaxEvents: true, // allow "more" link when too many events
                events: reservationsDict,

                eventClick: function (clickInfo) { },
            });

            // Send reservation ID when user clicks on a calendar event
            calendar.on('eventClick', function (clickInfo) {
                let reservationID = clickInfo.event.extendedProps.reservationID
                $.ajax({
                    method: "POST",
                    url: "/reservation/",
                    data: JSON.stringify({
                        id: reservationID,
                    }),
                    dataType: "json",
                    success: function (data) {
                        jsonData = JSON.parse(data)
                        // Format start date
                        let startDate = jsonData[0]["fields"]["start_date"].split("-")
                        let startDate2 = startDate[2] + "/" + startDate[1] + "/" + startDate[0]
                        // Format end date
                        let endDate = jsonData[0]["fields"]["end_date"].split("-")
                        let endDate2 = endDate[2] + "/" + endDate[1] + "/" + endDate[0]

                        // check if the user is the owner of the reservation
                        if (user_id == clickInfo.event.extendedProps.userID || is_admin == "yes") {
                            $('#modify-reservation-button').click()
                            // Insert the reservation data in the 'modify reservation' modal
                            let modifyModal = $("#staticBackdrop2")
                            modifyModal.find("#id_id").val(reservationID)
                            modifyModal.find("#id_name").val(jsonData[0]["fields"]["name"])
                            modifyModal.find("#id_start_date").val(startDate2)
                            modifyModal.find("#id_end_date").val(endDate2)
                            modifyModal.find("#id_description").val(jsonData[0]["fields"]["description"])

                            // Send a newajax request when a user clicks on the delete reservation button
                            $("#delete-reservation").on("click", function (e) {
                                $.ajax({
                                    method: "DELETE",
                                    url: "/delete_reservation/",
                                    data: JSON.stringify({
                                        id: reservationID,
                                    }),
                                    dataType: "json",
                                    success: function (data) {
                                        jsonData = JSON.parse(data)
                                        // Reload the window to update the calendar
                                        window.location.href = "/home/";
                                        window.location.href = "/agenda/";
                                    },
                                    error: function (data) { console.log("error") }
                                });
                            });

                        }
                        else {
                            $('#view-reservation-button').click()
                            // Insert the reservation data in the 'view reservation' modal
                            let viewModal = $("#staticBackdrop3")
                            viewModal.find("#view_name").empty().empty().append(jsonData[0]["fields"]["name"])
                            viewModal.find("#view_start_date").empty().append(startDate2)
                            viewModal.find("#view_end_date").empty().append(endDate2)
                            viewModal.find("#view_description").empty().append(jsonData[0]["fields"]["description"])
                        }
                    },
                    error: function (data) { console.log("error") }
                });
            });
            calendar.render();
        }
    }
    xmlhttp.open('GET', url, true)
    xmlhttp.send()

    // Make sure the calendar widget displays on top of the form modal window
    $(window).on('load', function () {
        let datePicker = document.getElementsByClassName('calendarbox module');
        let modalWindow = document.getElementById("staticBackdrop")
        let modalWindow2 = document.getElementById("staticBackdrop2")
        modalWindow.appendChild(datePicker[0])
        modalWindow.appendChild(datePicker[1])
        modalWindow2.appendChild(datePicker[2])
        modalWindow2.appendChild(datePicker[3])
    });

    // Resize the footer to match fixed calendar width on mobile devices
    if ($('#responsive-calendar').css('width') == "850px") {
        $('#layoutDefault_footer').css('width', '855px')
    };

    /* Make the calendar widget disappear when the user clicks outside of it
       Also makes sure not to open 2 calendars at once */
    $(window).on("click", function (e) {
        if (e.target.name == 'end_date' && ($('#calendarbox0').css('display') != 'block')) {
            $('#calendarbox1').css({ 'display': 'block', 'left': (e['pageX']), 'top': (e['pageY'] - 87) })
            $('#calendarbox3').css({ 'display': 'block', 'left': (e['pageX']), 'top': (e['pageY'] - 87) })
        }
        else if (e.target.name != 'start_date' && ($('#calendarbox0').css('display') == 'block')) {
            $('.calendar-cancel').children()[0].click()
            $('.calendar-cancel').children()[2].click()
        }
        else if (e.target.name == 'start_date' && ($('#calendarbox1').css('display') != 'block')) {
            $('#calendarbox0').css({ 'display': 'block', 'left': (e['pageX']), 'top': (e['pageY'] - 87) })
            $('#calendarbox2').css({ 'display': 'block', 'left': (e['pageX']), 'top': (e['pageY'] - 87) })
        }
        else if (e.target.name != 'end_date' && ($('#calendarbox1').css('display') == 'block')) {
            $('.calendar-cancel').children()[1].click()
            $('.calendar-cancel').children()[3].click()
        }
    });



});
