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

function getCurrentPageFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const page = parseInt(urlParams.get('page'), 10);
    if (isNaN(page)) {
        return page;
    } else {
        return 1;
    }
}

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
            // Update the product list with the new data
        });
}

$(document).ready(function() {
    console.log('Document ready. Trying to init selectpicker.');
    $('.selectpicker').selectpicker();
    console.log('Selectpicker initialized.');

    $('.update-button').click(function() {
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
});

