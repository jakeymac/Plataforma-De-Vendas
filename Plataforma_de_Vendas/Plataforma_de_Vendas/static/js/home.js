function load_data() {

    // TODO make an API call that will dynamically load these categories and sub-categories, 
    // along with each sub-category's products and add it to the page

    fetch('/api/products/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Error in request');
        }
    })
    .then(data => {
        console.log(data);
        let products = data.products;
        console.log(products);
        let productArea = $('#products-container');
        products.forEach(product => {
            productArea.append(`<div class="product-card">
                                <img src="${product.image}" alt="product-image">    
                                <a href="view_product/${product.id}"><h2 class="product-name-link">${product.name}</h2></a>
                                <p>$${product.price}</p>`);
        });
    })
}

function load_listeners() {
    $('.categories-list-item').hover(function() {
        // Hide all categories' sub-category containers, then show the one being hovered over
        $('.sub-categories-container').hide();
        var targetDivId = $(this).data('target');
        $("#" + targetDivId).show();
        
        // Update styling of all categories, then update the one being hovered over
        $('.categories-list-item').css('color', 'black');
        $(this).css('color', 'blue');
    });

    $('.sub-categories-list-item').hover(function() {
        // Hide all sub-categories' product containers, then show the one being hovered over
        $('.products-container').hide();
        var targetDivId = $(this).data('target');
        $("#" + targetDivId).show();

        // TODO add a call to the API to get the products that are being highlighted for the sub-category being hovered over

        // Update styling of all sub-categories, then update the one being hovered over
        $('.sub-categories-list-item').css('color', 'black');
        $(this).css('color', 'blue');

        
    })
}

$(document).ready(function() {
    $("#top-categories-list-container").show(); // Show the default categories list
    load_data();    
    load_listeners();
});