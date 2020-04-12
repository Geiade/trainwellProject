function swipeWeek(url, week) {
    console.log("ESTIIC")
    console.log(url, week)
    if (canSwipe(week) === false) return;

    $.ajax({
            url: url,
            data: {
                'week': week,
            },
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            },
            success: function (html) {
                $('#schedule').replaceWith(html);
            }
        }
    );
}

function canSwipe(week) {
    const date = new Date(); //Today
    let diff = date.getDate() - date.getDay() + (date.getDay() === 0 ? -6 : 1);
    const curr_monday = new Date(date.setDate(diff)).setHours(0, 0, 0, 0);

    let dateArr = week.toString().split("/");
    const req_date = new Date(parseInt(dateArr[2]), parseInt(dateArr[1]) - 1, parseInt(dateArr[0]));

    // Can't swipe before current week
    return req_date >= curr_monday;

}
