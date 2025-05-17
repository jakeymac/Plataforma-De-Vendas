function getFilterValues() {
    // Get the values of the filter elements with any user input
    let categoryFilterValue = $('#filter-categories').val();
    let sellerFilterValue = $('#filter-sellers').val();

    let filterValues = {};
    
    if (Array.isArray(categoryFilterValue) && categoryFilterValue.length > 0) {
        filterValues['category'] = categoryFilterValue;
    }

    if (Array.isArray(sellerFilterValue) && sellerFilterValue.length > 0) {
        filterValues['seller'] = sellerFilterValue;
    }

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

function buildQueryParams() {
    // Build the query parameters for the AJAX request
    let searchValue = getSearchValue();
    let sortValue = getSortValue();
    let filterValues = getFilterValues();

    console.log("Search value: ", searchValue);
    console.log("Sort value: ", sortValue);
    console.log("Filter values: ", filterValues);
    

    let params = {
        'search': searchValue,
        'sort': sortValue,
        'filter': filterValues,
    };

    return params;
}

function updateURL(params) {
    const newParams = new URLSearchParams(params);
    history.pushState({}, '', `${window.location.pathname}?${newParams}`);
}

function performSearch() {
    let params = buildQueryParams();
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
            console.log("Data received: ", data);
            // Update the product list with the new data
        })
}

$(document).ready(function() {
    console.log("Document ready. Trying to init selectpicker.");
    $('.selectpicker').selectpicker();
    console.log("Selectpicker initialized.");

    $(".update-button").click(function() {
        console.log("Update button clicked.");
        performSearch();
    })
});

