function getAffected(url, created, limit_date) {

    $.ajax({
            url: url,
            data: {
                'created': created,
                'limit_date': limit_date
            },
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            },
            success: function (html) {
                $('#notification').html("Reserves afectades:")
            }
        }
    );
}