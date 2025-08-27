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
    });
}

function load_listeners() {
    $("#search-button").click(() => {
        let searchText = $("#search-input-box").val();
        if (searchText) {
            window.location.href = `/product_search?search=${encodeURIComponent(searchText)}`;
        }
    });

    $('.categories-list-item').hover(function() {
        // Hide all categories' sub-category containers, then show the one being hovered over
        $('.sub-categories-container').hide();
        var targetDivId = $(this).data('target');
        $('#' + targetDivId).show();
        
        // Hide all product show case contaienrs
        $('.product-showcase-container').hide();
        
        // TODO have the first sub category's products show up by default

        // TODO fix so that hovering over the current main category doesn't hide the product show case container that's already open
        
        // Update styling of all categories, then update the one being hovered over
        $('.categories-list-item').css('color', 'black');
        $(this).css('color', 'blue');
    });

    $('.sub-categories-list-item').hover(function() {
        // Hide all sub-categories' product containers, then show the one being hovered over
        $('.product-showcase-container').hide();
        var targetDivId = $(this).data('target');
        $('#' + targetDivId).show();

        // Update styling of all sub-categories, then update the one being hovered over
        $('.sub-categories-list-item').css('color', 'black');
        $(this).css('color', 'blue');

        // TODO add a call to the API to get the products that are being highlighted for the sub-category being hovered over
        
        // Hide all product show case contaienrs
        $('.product-showcase-container').hide();
        var targetDiv = $(this).data('target');
        $('#' + targetDiv).show();
    });
    
}

$(document).ready(() => {
    $('#top-categories-list-container').show(); // Show the default categories list
    load_data();    
    load_listeners();
});