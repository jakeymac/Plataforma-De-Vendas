function load_data() {
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
$(document).ready(function() {
    load_data();    
});