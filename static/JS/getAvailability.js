var selected_hours = [];

$(function () {

    $('[id^=selectable-content]').selectable({
        filter: ".selectable", // Exclude booked_dates and holidays.

        selecting: function (event, ui) {
            let curr_selectable = $(this).attr('id');
            for (const x of Array(7).keys()) {
                let qs = $('#selectable-content' + x);
                if (curr_selectable !== ('selectable-content' + x)) {
                    // Refresh other selectables, except me.
                    qs.selectable("widget").children().removeClass('ui-selected');
                }
            }
        },

        stop: function (event, ui) {
            selected_hours = [];
            $(".ui-selected", this).each(function () {
                let curr = $(this).attr("id").split(",");
                selected_hours.push(curr);
            });

            // Check availability for each field in selected hours.
            if (selected_hours.length > 1) {
                var last = selected_hours.pop() //Unnecessary to check last.
                checkFieldAvailability(selected_hours, last);
            }
        }
    });


});

function checkFieldAvailability(date, last) {

    let week_avail = avail
    let booked_date = date[0][0];
    let desired_hours = [];
    let field_avail = {};
    let book_avail = {};

    date.forEach(element => desired_hours.push(element[1]));

    for (const [key, value] of Object.entries(week_avail)) {
        let curr = key.split(',');
        if (booked_date === curr[0]) {
            field_avail[key] = value;
        }
    }

    for (const x in desired_hours) {
        for (const [key, value] of Object.entries(field_avail)) {
            if (value.includes(desired_hours[x])) {
                let curr = key.split(',')[1];

                if (curr in book_avail)
                    book_avail[curr].push(desired_hours[x]);
                else
                    book_avail[curr] = [desired_hours[x]];
            }
        }
    }

    launchModal(date, book_avail, last);
}


function launchModal(date, availability, last) {

    $('#fieldsModal').on("show.bs.modal", function () {
        let modal = $(this);
        // Parsed to avoid conflicts between django vars an JS.
        let dateArr = date[0][0].toString().split("/");
        const req_date = new Date(parseInt(dateArr[2]), parseInt(dateArr[1]) - 1, parseInt(dateArr[0]));

        let month_name = function (dt) {
            mlist = ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"];
            return mlist[dt.getMonth()];
        };

        modal.find('.modal-title').attr('id', date[0][0])
        modal.find('.modal-title').html('<i class="far fa-calendar-alt mr-3"></i>' +
            month_name(req_date) + " " + req_date.getDate() + ", " + req_date.getFullYear() +
            '<br>' + '<small>' + date[0][1] + '-' + last.toString().split(",")[1] + '</small>');

        modal.find('.modal-body').empty();
        for (const [key, value] of Object.entries(availability)) {
            modal.find('.modal-body').append('<label class="mb-2" for="' + key + '">' + key + '</label>');

            let curr_opts = "";
            for (const v in value) {
                curr_opts += '<option>' + value[v] + '</option>';
            }
            // curr_opts += '<option>'+last+'</option>';

            modal.find('.modal-body').append('<select multiple data-actions-box="true" ' +
                'class="form-control selectpicker mb-2"' + 'id="' + key + '">' + curr_opts + '</select>');

            $('.selectpicker').selectpicker('render');

        }
    }).modal('show');
}


function generateSelection() {
    let selection = {}

    $('.selectpicker').each(function (index) {
        selection[$(this).attr('id')] = [$(this).val(), $('.modal-title').attr('id')]
    })
    let hours = []
    const _arr = Object.values(selection).reduce((k, v) => k.concat(v[0]), [])
    selected_hours.forEach(e => hours.push(e[1]))

    if (_arr.length === hours.length && hours.every(element => _arr.includes(element))) {
        $('#json_data').val(JSON.stringify(selection)).appendTo('#book_form');
        $("#book_form").submit();
    } else alert("Make sure you select an hour once.")


}