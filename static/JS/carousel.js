$(document).ready(function () {
    $('.installations').slick({
        prevArrow: "<i style=\"color: #f58b3c\" class=\"fas fa-chevron-left\"></i>",
        nextArrow: "<i style=\"color: #f58b3c\" class=\"fas fa-chevron-right\"></i>",
        infinite: true,
        speed: 1000,
        autoplay: true,
        autoplaySpeed: 2000,
        slidesToShow: 4,
        slidesToScroll: 4,
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: 3,
                    slidesToScroll: 3,
                    infinite: true,
                }
            },
            {
                breakpoint: 600,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 2
                }
            },
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                }
            }
        ]
    });
});