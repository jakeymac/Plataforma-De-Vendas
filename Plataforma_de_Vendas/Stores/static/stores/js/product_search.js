function getFilterValues() {
    // Get the values of the filter elements with any user input
    let filterValues = {};
    let filterSelectors = $('select.filter-selector');
    filterSelectors.each(function() {
        let filterName = $(this).attr('name').split('filter-')[1];
        let value = $(this).val();
        if (value) { // Check if the value is not empty
            filterValues[filterName] = value;
        }
    });

    return filterValues;
}

function getSearchValue() {
    // Get the value of the search input
    let searchValue = $('#product-text-search').val();
    return searchValue;
}

function getSortValue() {
    // Get the value of the sort select
    let sortValue = $('#sort-products').val();
    return sortValue;
}

function buildQueryParams(page = 1) {
    // Build the query parameters for the AJAX request
    let searchValue = getSearchValue();
    let sortValue = getSortValue();
    let filterValues = getFilterValues();

    console.log('Search value: ', searchValue);
    console.log('Sort value: ', sortValue);
    console.log('Filter values: ', filterValues);
    

    let params = {
        search: searchValue,
        sort: sortValue,
        page: page,
        filters: JSON.stringify(filterValues),
    };

    return params;
}

function updateURL(params) {
    const newParams = new URLSearchParams(params);
    history.pushState({}, '', `${window.location.pathname}?${newParams}`);
}

// TODO will use this in pagin
// function getCurrentPageFromURL() {
//     const urlParams = new URLSearchParams(window.location.search);
//     const page = parseInt(urlParams.get('page'), 10);
//     if (isNaN(page)) {
//         return page;
//     } else {
//         return 1;
//     }
// }

function performSearch(page = 1) {
    let params = buildQueryParams(page);
    updateURL(params);
    let query = new URLSearchParams(params);
        fetch(`/api/products/search/?${query}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Data received: ', data);
            $("#inner-products-container").empty();
            if (data.products.length > 0) {
                data.products.forEach(product => {
                    let productHTML = productCardHTML(product);
                    $("#inner-products-container").append(productHTML);
                });
            } else {
                $("#inner-products-container").append('<p>No products found.</p>');
            }
        });
}

function productCardHTML(product) {
    // TODO add a generic product image with "onerror" if the image can't be loaded
    return `
    <div class="col">
        <div class="col product-card h-100 shadow-sm">
            <img class="product-card-img" src="${product.product_images[0].image}" alt="${product.product_name}" loading="lazy"> 
            <div class="product-card-body d-flex flex-column">
            <div class="product-title-wrapper">
                <h6 class="product-card-title" title="${product.product_name}">${product.product_name}</h6>
            </div>
                 <a href="/view_product/${product.id}/" class="btn btn-outline-secondary">View Product</a>
            </div>
        </div>
    </div>
    `;
}

$(document).ready(() => {
    console.log('Document ready. Trying to init selectpicker.');
    $('.selectpicker').selectpicker();
    console.log('Selectpicker initialized.');

    $('#clear-filter-button').click(() => {
        let filterSelectors = $('select.filter-selector');
        filterSelectors.each(function() {
            $(this).find('option').prop('selected', false);
            $(this).selectpicker('val', []);
        });
    })

    $('.update-button').click(() => {
        console.log('Update button clicked.');
        performSearch();
    });
    
    // TODO implement these buttons - with disabling/enabling buttons
    // $('#next-page-button').click(function() {
    //     let currentPage = getCurrentPageFromURL();
    //     performSearch(currentPage + 1);
    // })
    // $('#previous-page-button').click(function() {
    //     let currentPage = getCurrentPageFromURL();
    //     if (currentPage > 1) {
    //         performSearch(currentPage - 1);
    //     }
    // })
    console.log("Performing initial search.");
    performSearch(1);
});

