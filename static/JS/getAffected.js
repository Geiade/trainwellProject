function getAffected(url, created) {

    let values = {};
    $.each($('#formulari').serializeArray(), function (i, field) {
        if (field.name == 'places') {
            values[field.name] += field.value + ','

        } else {
            values[field.name] = field.value;
        }

    });
    if (values['disabled']) {
        $.ajax({
                url: url,
                data: {
                    'created': created,
                    'limit_date': values['limit_date'],
                    'places': values['places'].replace('undefined', '')
                },
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                success: function (data) {
                    let resultat = confirm('Bookings affected: ' + data)

                    if (resultat)
                        $('#formulari').submit()
                    else
                        return false
                }
            }
        );
    }
    else {
        $('#formulari').submit()
    }
}