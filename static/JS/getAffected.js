function getAffected(url, created) {

    let form = $('#formo');
    let values = buildForm(form)

    if (values['disabled']) {

        $.ajax({
                url: url,
                data: {
                    'created': created,
                    'limit_date': values['limit_date'],
                    'places': values['places'].toString()
                },
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                success: function (data) {
                    formatAlertBox(form, data)
                }
            }
        );
    }
    else form.submit()
}

function getAffectedByEvent(url, created) {
    let places = curr_places
    let form = $('#event_form');
    let values = buildForm(form)
    let are_included = false

    if (values['places'] != undefined) are_included = places.every(x => values['places'].includes(x))

    if (are_included === true) {
        form.submit();
    } else {
        let now = new Date()
        now.setFullYear(now.getFullYear() + 2)
        $.ajax({
                url: url,
                data: {
                    'created': created,
                    'limit_date': now.getFullYear() + '-' + (now.getMonth() + 1) + '-' + now.getDate(),
                    'places': values['places'].toString()
                },
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                success: function (data) {
                    formatAlertBox(form, data);
                }
            }
        );
    }
}

function buildForm(form) {
    let values = {}
    $.each(form.serializeArray(), function (i, field) {
        if (field.name === 'places') {
            if (field.name in values) values[field.name].push(field.value)
            else values[field.name] = [field.value];
        } else values[field.name] = field.value;
    });

    return values
}

function formatAlertBox(form, data) {
    let data_asjson = JSON.parse(data);

    let html = "";
    let e;

    html = "<ul>"
    for (e in data_asjson) {
        html += "<li>"
        let booking = data_asjson[e];
        html += booking[0] + " " + booking[1] + ", " + booking[4]
        html += "<ul>" + "<li> Event: " + booking[2] + "</li>" + "<li> Phone: " + booking[3] + "</li></ul>"
        html += "</li>"
    }
    html += "</ul>"

    let bookings_id = []
    data_asjson.map(function (curr) {
        bookings_id.push(curr[5]);
    })

    bootbox.confirm({
        title: "Bookings affected" + "<sup>" + data_asjson.length + "</sup>",
        message: html,
        callback: function (result) {
            if (result) {
                $('#bookings_affected').attr('value', bookings_id)
                form.submit();
            }
        }
    });
}
