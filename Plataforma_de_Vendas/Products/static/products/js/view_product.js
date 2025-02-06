function loadData() {
    // TODO Add a loading animation here for images loading
    fetch(`/api/products/images/${productId}/`)
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            // TODO add errors to the page
            console.error('Error loading images: ', response.json());
        } 
    })
    .then(data => {
        if (data.images && data.images.length > 0) {
            let images = data.images;

            $('#main-image-container').append(
                `<img id="main-image" src="${images[0].url}" alt="Product Image">`
            );

            for (let image of images) {
                $('#thumbnail-carousel').append(
                    `<div class="thumbnail-image-container">
                        <img class="thumbnail-image" src="${image.url}" alt="Product Image">
                    </div>`
                );
            }

            $('#thumbnail-carousel').slick({
                vertical: true,
                slidesToShow: 4,
                slidesToScroll: 1,
                arrows: true,
                infinite: false,
                prevArrow: `<button type="button" class="slick-prev">
                                <i class="bi bi-arrow-up"></i>
                            </button>`,
                nextArrow: `<button type="button" class="slick-next">
                                <i class="bi bi-arrow-up"></i>
                            </button>`
            });
            
            // This is a simple workaround for a bug with slick, where the arrows are focused when clicked.
            // This would cause the buttons to dissapear after clicking on them until clicking somehwere else on the page. 
            $('.slick-prev, .slick-next').on('mousedown', (e) => {
                e.preventDefault();
            });

            $('.thumbnail-image').on('click', function () {
                $('#main-image').attr('src', $(this).attr('src'));
            });
            
        } else {
            // TODO add an image here or proper text here for if a product has no images
            console.log('No images found');
            // <img id="main-image" src="{% static 'images/no_image_available.png' %}" alt="Product Image">

        }
    })
    .catch(error => {
        console.error('Error loading images: ', error);
        // $("#initial-image-loading-container").hide();
        // $("#inner-images-messages-label").text("Error loading images");
        // $("#inner-images-messages-label").addClass("error-message-div");
        // $("#inner-images-messages-label").show();
    });
}

$(document).ready(() => {
    loadData();
});