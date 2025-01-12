function loadData() {

}

$(document).ready(function () {
    $("#thumbnail-carousel").slick({
        vertical: true,
        slidesToShow: 4,
        slidesToScroll: 1,
        arrows: true,
        infinite: false,
        prevArrow: '<button type="button" class="slick-prev"><i class="bi bi-arrow-up"></i></button>',
        nextArrow: '<button type="button" class="slick-next"><i class="bi bi-arrow-up"></i></button>'
    });

    // This is a simple workaround for a bug with slick, where the arrows are focused when clicked.
    // This would cause the buttons to dissapear after clicking on them until clicking somehwere else on the page. 
    $(".slick-prev, .slick-next").on("mousedown", function (e) {
        e.preventDefault();
    });
});