function getAffected(url, created) {

    let values = {};
    let form = $('#formo');
    $.each(form.serializeArray(), function (i, field)
    {
        if (field.name === 'places') values[field.name] += field.value + ','
        else values[field.name] = field.value;
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
                    if (confirm('Bookings affected: ' + data)) form.submit()
                    else return false
                }
            }
        );
    }
    else form.submit()
}