// Variables to manage the Choices dropdown objects
var categoryFilterChoices;
var subcategoryFilterChoices;

function clearFilters() {
    categoryFilterChoices.removeActiveItems();
    subcategoryFilterChoices.removeActiveItems();
}

function getFilterValues() {
    // Get the values of the filter elements with any user input
    let filterValues = {};

    let categoriesValues = categoryFilterChoices.getValue(true);
    let subcategoriesValues = subcategoryFilterChoices.getValue(true);

    if (categoriesValues.length > 0) {
        filterValues['categories'] = categoriesValues;
    }
    if (subcategoriesValues.length > 0) {
        filterValues['subcategories'] = subcategoriesValues;
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

function buildQueryParams(overrides = {}, page = 1) {
    // Build the query parameters for the AJAX request

    var currentUrlParams = new URLSearchParams(window.location.search);
    var newParams = {};

    if (currentUrlParams.has('search')) {
        newParams.search = currentUrlParams.get('search');
    }

    if (currentUrlParams.has('sort')) {
        newParams.sort = currentUrlParams.get('sort');
    }

    if (currentUrlParams.has('filters')) {
        newParams.filters = currentUrlParams.get('filters');
    }

    if (currentUrlParams.has('page')) {
        newParams.page = parseInt(currentUrlParams.get('page'), 10);
    }

    if ('search' in overrides) {
        newParams.search = overrides.search;
    }

    if ('sort' in overrides) {
        newParams.sort = overrides.sort;
    }

    if ('filters' in overrides) {
        newParams.filters = JSON.stringify(overrides.filters);
    }

    if ('page' in overrides) {
        newParams.page = overrides.page;
    }
    
    return newParams;
}

function updateURL(params) {
    const urlParams = new URLSearchParams();

    if (params.search && params.search.trim() !== '') {
        urlParams.set('search', params.search.trim());
    }
    if (params.sort && params.sort.trim() !== '') {
        urlParams.set('sort', params.sort.trim());
    }
    if (params.page && params.page !== 1) {
        urlParams.set('page', params.page);
    }

    try {
        const filters = JSON.parse(params.filters || '{}');
        if (Object.keys(filters).length > 0) {
            urlParams.set('filters', JSON.stringify(filters));
        }
    } catch (e) {
        console.warn('Invalid filters JSON:', e);
    }

    const queryString = urlParams.toString();
    const newUrl = queryString ? `${window.location.pathname}?${queryString}` : window.location.pathname;
    history.pushState({}, '', newUrl);
}

function getCurrentPageFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const page = parseInt(urlParams.get('page'), 10);
    if (isNaN(page)) {
        return 1;
    } else {
        return page;
    }
}

function performSearch(overrides = {}, page = 1) {
    let params = buildQueryParams(overrides, page);
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
        $('#inner-products-container').empty();
        if (data.products.length > 0) {
            data.products.forEach(product => {
                let productHTML = productCardHTML(product);
                $('#inner-products-container').append(productHTML);
            });
            if (data.previous_page) {
                $('#previous-page-button').removeClass('disabled');
            } else {
                $('#previous-page-button').addClass('disabled');
            }

            if (data.next_page) {
                $('#next-page-button').removeClass('disabled');
            }
            else {
                $('#next-page-button').addClass('disabled');
            }

        } else {
            $('#inner-products-container').append('<p>No products found.</p>');
        }
    });
}

function productCardHTML(product) {
    let imageUrl;
    if (product.product_images.length > 0) {
        imageUrl = product.product_images[0].image;
    } else {
        imageUrl = `${STATIC_URL}stores/images/missing_image_placeholder.png`;
    }
    return `<div class="col">
                <div class="col product-card h-100 shadow-sm">
                    <img class="product-card-img" 
                     src="${imageUrl}" 
                     alt="${product.product_name}" 
                     loading="lazy"
                     onerror="this.onerror=null;this.src='${STATIC_URL}stores/images/missing_image_placeholder.png';"> 
                    <div class="product-card-body d-flex flex-column">
                    <div class="product-title-wrapper">
                        <h6 class="product-card-title" title="${product.product_name}">${product.product_name}</h6>
                    </div>
                        <a href="/view_product/${product.id}/" class="btn btn-outline-secondary">View Product</a>
                    </div>
                </div>
            </div>`;
}

$(document).ready(() => {
    console.log('Document ready. Trying to init selectpicker.');
    $('.selectpicker').selectpicker();
    console.log('Selectpicker initialized.');

    $('#clear-filter-button').click(() => {
        clearFilters();
        performSearch(overrides={filters: {}})
    });

    $("#search-button").click(() => {
        console.log('Search button clicked.');
        let searchValue = getSearchValue();
        performSearch(overrides={search: searchValue});
    });

    $("#sort-products-button").click(() =>{
        console.log('Sort button clicked.');
        let sortValue = getSortValue();
        performSearch(overrides={sort: sortValue});
    });
    
    $("#apply-filter-button").click(() => {
        console.log('Apply filter button clicked.');
        let filterValues = getFilterValues();
        performSearch(overrides={filters: filterValues});
    });
    
    $('#next-page-button').click(() => {
        let currentPage = getCurrentPageFromURL();
        performSearch({}, currentPage + 1);
    });

    $('#previous-page-button').click(() => {
        let currentPage = getCurrentPageFromURL();
        if (currentPage > 1) {
            performSearch({}, currentPage - 1);
        }
    });
    categoryFilterChoices = new Choices('#filter-categories', {
        removeItemButton: true,
        itemSelectText: '',
        searchEnabled: true,
        placeholder: true,
        placeholderValue: 'Choose a category...',
    });
    subcategoryFilterChoices = new Choices('#filter-subcategories', {
        removeItemButton: true,
        itemSelectText: '',
        searchEnabled: true,
        placeholder: true,
        placeholderValue: 'Choose a subcategory...',
    });

    console.log('Performing initial search.');
    performSearch({}, page=1); // TODO make sure this works when loading the page with search parameters provided
    
});
