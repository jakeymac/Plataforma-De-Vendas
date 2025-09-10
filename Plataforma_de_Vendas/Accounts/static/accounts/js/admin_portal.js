// Dict to use for form fetch calls
const apiUrls = {
    'add-category-form': ['/api/products/categories/add/', 'POST'], 
    'add-subcategory-form': ['/api/products/subcategories/add/', 'POST'],
    'edit-category-form': ['/api/products/categories/update/', 'PUT'],
    'edit-subcategory-form': ['/api/products/subcategories/update/', 'PUT'],
    'top-categories-form': ['/api/products/topsubcategories/update/', 'PUT']
};

const formSuccessMessages = {
    'add-category-form': 'Category added successfully',
    'add-subcategory-form': 'Subcategory added successfully',
    'edit-category-form': 'Category updated successfully',
    'edit-subcategory-form': 'Subcategory updated successfully',
    'top-categories-form': 'Top categories updated successfully'
}

function update_product_selector(products) {
    $('#product-selector').empty();
    if (products.length === 0) {
        $('#product-selector').append('<option value="">No products found</option>');
    } else {
        $('#product-selector').append('<option value="">Select a product</option>');
        products.forEach(product => {
            $('#product-selector').append(`<option value="${product.id}">${product.product_name}</option>`);
        });
    }
}

function load_listeners() {
    $('.form-control').on('input', function () {
        const inputId = $(this).attr('id');
        // Remove error class and clear error message
        $(`#${inputId}`).removeClass('error-input');
        $(`#${inputId}_error_container`).text('');
    });

    $('.form-select').on('change', function () {
        const selectId = $(this).attr('id');
        // Remove error class and clear error message
        $(`#${selectId}`).removeClass('error-input');
        $(`#${selectId}_error_container`).text('');
    });

    $('.top-subcategory-selector').on('change', function () {
        const selectId = $(this).attr('id');
        $(`#${selectId}`).removeClass('error-input');

        // Check if all the selectors have been fixed
        if ($('.top-subcategory-selector.error-input').length == 0) {
            $('#top-categories-message-container').removeClass('alert alert-danger');
            $('#top-categories-message-container').text('');
        }
    });

    $('.delete-button').click(function () {
        let deleteType = $(this).data('type');
        let deleteId = $(`#edit_${deleteType}_selector`).val();
        let deleteItemName = $(`#edit_${deleteType}_selector option:selected`).text();

        let pluralDeleteTypes = {'category': 'categories', 'subcategory': 'subcategories'};
        let pluralDeleteType = pluralDeleteTypes[deleteType]; // To use in the endpoint URL

        if (deleteId != '') {
            $('#confirm-deletion-modal').modal('show');
            $('#confirm-deletion-main-text').text(`Are you sure you want to delete ${deleteType} ${deleteItemName}?`);
            $('#confirm-deletion-button').on('click', async () => {
                let endpointUrl = `/api/products/${pluralDeleteType}/remove/${deleteId}/`;
                try {
                    let response = await fetch(endpointUrl, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': csrfToken
                        }
                    });
                    if (!response.ok) {
                        $('#confirm-deletion-main-text').text(`There was an error trying to delete the ${deleteType}`);
                        $('#confirm-deletion-main-text').addClass('error-message');
                        setTimeout(() => {
                            $('#confirm-deletion-main-text').text(`Are you sure you want to delete ${deleteType} ${deleteItemName}?`);
                            $('#confirm-deletion-main-text').removeClass('error-message');
                        }, 2000);
                    } else {
                        $('#confirm-deletion-main-text').text(`The ${deleteType} was successfully deleted`);
                        $('#confirm-deletion-main-text').addClass('deletion-success-message');
                        setTimeout(() => {
                            window.location.reload();
                        }, 2000);
                    }
                } catch {
                    $('#confirm-deletion-main-text').text(`There was an error trying to delete the ${deleteType}`);
                    $('#confirm-deletion-main-text').addClass('error-message');
                    setTimeout(() => {
                        $('#confirm-deletion-main-text').text(`Are you sure you want to delete ${deleteType} ${deleteItemName}?`);
                        $('#confirm-deletion-main-text').removeClass('error-message');
                    }, 2000);
                }
            });
        } else {
            $(`#edit-${deleteType}-message-container`).text(`Please select a ${deleteType}`);
            setTimeout(() => {
                $(`#edit-${deleteType}-message-container`).text('');
            }, 2000);
        }
    });

    $('form').submit(async function (e) {
        e.preventDefault();
        const formData = new FormData(this);
        const formId = $(this).attr('id');
        const formUrl = apiUrls[formId][0];
        var method = apiUrls[formId][1];
        try {
            const response = await fetch(formUrl, {
                method: method,
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData 
            });

            if (!response.ok) {
                const errorData = await response.json();
                for (var field in errorData) {
                    if (formId.includes('edit')) {
                        $(`#edit_${field}_error_container`).text(errorData[field]);
                        $(`#edit_${field}`).addClass('error-input');
                    } else if (formId.includes('add')) {
                        $(`#${field}_error_container`).text(errorData[field]);
                        $(`#${field}`).addClass('error-input');
                    } else {
                        // This is for the top categories form
                        if (errorData.duplicates) {
                            for (var orderNum in errorData.duplicates) {
                                $(`#top_subcategory_selector_${orderNum}`).addClass('error-input');
                            }
                        }
                        $('#top-categories-message-container').text(errorData.message);
                        $('#top-categories-message-container').addClass('alert alert-danger');
                    }
                }            
            } else {
                // Show success message
                let successMessage = formSuccessMessages[formId];
                $(this).find('.message-container').text(successMessage);
                $(this).find('.message-container').addClass('alert alert-success');

                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            }
        } catch (error) {
            $(this).find('.message-container').text('Error: ' + error.message);
            $(this).find('.message-container').addClass('alert alert-danger');
        }
    });    

    $('#product-selector').on('change', function () {
        // Clear out any error messages below 
        $("#product-message-container").removeClass('alert alert-danger');
        $("#product-message-container").text('');
    });

    $('#edit-product-button').on('click', () => {
        let productId = $('#product-selector').val();
        if (productId == '') {
            $('#product-message-container').removeClass('alert alert-danger');
            $('#product-message-container').text('Please select a product to edit');
        } else {
            // Check for product's existence to avoid errors
            fetch(`/api/products/${productId}/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => {
                if (!response.ok) {
                    if (response.status === 404) {
                        $('#product-message-container').addClass('alert alert-danger');
                        $('#product-message-container').text('Product not found');
                    } else {
                        $('#product-message-container').addClass('alert alert-danger');
                        $('#product-message-container').text('An error occurred');
                    }
                } else {
                    window.location.href = '/edit_product/' + productId;
                }
            });
        }
    });

    $('#view-product-button').on('click', () => {
        let productId = $('#product-selector').val();
        if (productId == '') {
            $('#product-message-container').removeClass('alert alert-danger');
            $('#product-message-container').text('Please select a product to view');
        } else {
            // Check for product's existence to avoid errors
            fetch(`/api/products/${productId}/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => {
                if (!response.ok) {
                    if (response.status === 404) {
                        $('#product-message-container').addClass('alert alert-danger');
                        $('#product-message-container').text('Product not found');
                    } else {
                        $('#product-message-container').addClass('alert alert-danger');
                        $('#product-message-container').text('An error occurred');
                    }
                } else {
                    window.location.href = '/view_product/' + productId;
                }
            });
        }
    });
    
    $('#edit_category_selector').change(function () {
        let category = categories.find(cat=> cat.id == $(this).val()); // Uses the categories object pulled from the context in a script in the template
        $('#edit_category_name').val(category.category_name);
        $('#edit_category_description').val(category.category_description);
    });

    $('#edit_subcategory_selector').change(function() {
        let subcategory = subcategories.find(subcat=> subcat.id == $(this).val()); // Uses the subcategories object pulled from the context in a script in the template
        $('#edit_subcategory_name').val(subcategory.subcategory_name);
        $('#edit_subcategory_description').val(subcategory.subcategory_description);
        $('#edit_subcategory_category_selector').val(subcategory.category_id);
    });

    $('#product-search').on('input', function () {
        // Clear out any error messages below 
        $("#product-message-container").removeClass('alert alert-danger')
        $("#product-message-container").text('');

        let searchTerm = $(this).val();
        let filteredProducts = products.filter(product => {
            return product.product_name.toLowerCase().includes(searchTerm) || (product.product_description && product.product_description.toLowerCase().includes(searchTerm));
        });
        update_product_selector(filteredProducts);
    });
}

$(document).ready(() => {
    load_listeners();
});