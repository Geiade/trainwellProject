function swipeBookings(type, len) {

    switch (type) {
        case 1:
            $(".paid").css("display", "")
            $(".notpaid").css("display", "none")
            $(".cancelled").css("display", "none")
            $(".all").css("display", "none")
            $("#num_books").html(len)
            break;
        case 2:
            $(".paid").css("display", "none")
            $(".notpaid").css("display", "")
            $(".cancelled").css("display", "none")
            $(".all").css("display", "none")
            $("#num_books").html(len)
            break;
        case 3:
            $(".paid").css("display", "none")
            $(".notpaid").css("display", "none")
            $(".cancelled").css("display", "")
            $(".all").css("display", "none")
            $("#num_books").html(len)
            break;
        default:
            $(".paid").css("display", "none")
            $(".notpaid").css("display", "none")
            $(".cancelled").css("display", "none")
            $(".all").css("display", "")
            $("#num_books").html(len)
    }
}