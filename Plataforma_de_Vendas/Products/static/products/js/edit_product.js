// Debounce timer for auto-saving
// TODO make sure auto save isn't on while images are uploading

let autoSaveTimeout;
let uploadInProgress = false;

function addNewPropertyRow() {
    $('#product-properties').append(`
        <div class="row sortable-item property-row" id="property-row-${propertyCounter}">
            <div class="col-5">
                <label for="property-name-${propertyCounter}" class="form-label">Property Name</label>
                <input type="text" class="form-control product-info-input property-name-input" id="property-name-${propertyCounter}" name="property-name-${propertyCounter}">
                <div class="error-message-div property-name_error_field" id="property-name-${propertyCounter}_error_field"></div>
            </div>
            <div class="col-5">
                <label for="property-value-${propertyCounter}" class="form-label">Property Value</label>
                <input type="text" class="form-control product-info-input property-value-input" id="property-value-${propertyCounter}" name="property-value-${propertyCounter}">
                <div class="error-message-div property-value_error_field" id="property-value-${propertyCounter}_error_field"></div>
            </div>
            <div class="col-2">
                <button type="button" class="btn btn-danger remove-property-button">Remove</button>
            </div>
        </div>`);
    propertyCounter++;
    bindPropertyRemovalButtons();
}

function addNewPriceRow() {
    $('#product-prices').append(`
        <div class="col-12 sortable-item row price-row" id="price-row-${priceCounter}">
            <div class="col-4">
                <label for="price-${priceCounter}" class="form-label">Price</label>
                <input type="number" class="form-control product-info-input price-input" id="price-${priceCounter}" name="price-${priceCounter}">
                <div class="error-message-div price_error_field" id="price-${priceCounter}_error_field"></div>
            </div>
            <div class="col-4">
                <label for="quantity-${priceCounter}" class="form-label">Quantity</label>
                <input type="number" class="form-control product-info-input quantity-input" id="quantity-${priceCounter}" name="quantity-${priceCounter}">
                <div class="error-message-div quantity_error_field" id="quantity-${priceCounter}_error_field"></div>
            </div>
            <div class="col-4">
                <button type="button" class="btn btn-danger remove-price-button">Remove</button>
            </div>
        </div>`);
    priceCounter++;
    bindPriceRemovalButtons();
}

function addNewImageRow(imageUrl, imageId, isInitial=false) {
    $('#inner-images-messages-label').text('');
    $('#inner-images-messages-label').hide();

    let newImageRow = `<div class="row image-row">
                            <div class="col-12 image-row-inner-container sortable-item">
                                <div class="col-6 product-image-container" id="product-image-${imageId}-container">
                                    <img src="${imageUrl}" alt="Product Image" class="product-image">
                                </div>
                                <div class="col-6 remove-image-button-container">
                                    <button type="button" class="btn btn-danger remove-image-button" id="remove-image-${imageId}">Remove Image</button>
                                </div>
                                <input type="hidden" name="image_id" id="image_id" value="${imageId}">
                            </div>
                        </div>`;
    $('#images-inner-container').append(newImageRow); 
    if (!isInitial) {
        $('.image-row').show();
    }   
    $(`#remove-image-${imageId}`).on('click', function() {
        let imageId = $(this).closest('.image-row').find('#image_id').val();
        console.log(imageId);
        fetch(`/api/products/remove_image/${imageId}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (response.ok) {
                $(this).closest('.image-row').remove();
                if ($('.image-row').length === 0) {
                    $('#inner-images-messages-label').text('No images have been added for this product');
                    $('#inner-images-messages-label').removeClass('error-message-div');
                    $('#inner-images-messages-label').show();
                }
                clearTimeout(autoSaveTimeout);
                autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
            } else {
                console.error('Error removing image: ', response.json());
                $('#inner-images-messages-label').text('Error removing image');
                $('#inner-images-messages-label').addClass('error-message-div');
                $('#inner-images-messages-label').show();
                setTimeout(() => {
                    $('#inner-images-messages-label').text('');
                    $('#inner-images-messages-label').hide();
                }, 2000);
            }
        });
    });
}

function loadData() {
    // Load the product images
    $('#initial-image-loading-icon-container').show();
    fetch(`/api/products/images/${productId}/`)
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            console.error('Error loading images: ', response.json());
            $('#initial-image-loading-icon-container').hide();
            $('#inner-images-messages-label').text('Error loading images');
            $('#inner-images-messages-label').addClass('error-message-div');
            $('#inner-images-messages-label').show();
        } 
    })
    .then(data => {
        if (data.images && data.images.length > 0) {
            let images = data.images;
            let imagesLoaded = 0;
            var totalImages = images.length;

            for (let image of images) {
                addNewImageRow(image.url, image.id, true);
                // TODO look into fixing this, if there are any issues with loading, no images will be shown
                $(`#product-image-${image.id}-container img`).on('load', () => {
                    imagesLoaded++;
                    console.log(imagesLoaded);
                    if (imagesLoaded === totalImages) {
                        $('#initial-image-loading-icon-container').hide();
                        $('.image-row').show();   
                        $('#images-inner-container').sortable({
                            placeholder: 'sortable-placeholder',
                            start: function (e, ui) {
                                // Optionally adjust placeholder height to match dragged element
                                ui.placeholder.height(ui.item.outerHeight());
                                ui.placeholder.css('margin-bottom', ui.item.css('margin-bottom'));
                                ui.placeholder.css('margin-top', ui.item.css('margin-top'));
                                ui.item.siblings('.sortable-item').each(function () {
                                    $(this).css({
                                        'margin-top': $(this).css('margin-top'),
                                        'margin-bottom': $(this).css('margin-bottom')
                                    });
                                });
                            }
                        });
                    }
                });
            }
            $('#initial-image-loading-icon-container').hide();
        } else {
            $('#inner-images-messages-label').text('No images have been added for this product');
            $('#inner-images-messages-label').show();
        }
        $('#initial-image-loading-icon-container').hide();

    })
    .catch(error => {
        console.error('Error loading images: ', error);
        $('#initial-image-loading-icon-container').hide();
        $('#inner-images-messages-label').text('Error loading images');
        $('#inner-images-messages-label').addClass('error-message-div');
        $('#inner-images-messages-label').show();
    });
}

function loadListeners() {
    $('#add-property-button').on('click', () => {
        // Grab the last property row in the form and check if it has values, otherwise don't add a new row
        let lastPropertyRow = $('#product-properties .sortable-item:last');
        if (lastPropertyRow.length > 0) {
            let propertyName = lastPropertyRow.find('.property-name-input').val().trim();
            let propertyValue = lastPropertyRow.find('.property-value-input').val().trim();
            if (propertyName || propertyValue) {
                addNewPropertyRow();
                clearTimeout(autoSaveTimeout);
                autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
            }
        // If there are no property rows, add one
        } else {
            addNewPropertyRow();
        }
    });

    $('#add-price-button').on('click', () => {
        // Grab the last price row in the form and check if it has values, otherwise don't add a new row
        let lastPriceRow = $('#product-prices .sortable-item:last');
        if (lastPriceRow.length > 0) {
            let price = lastPriceRow.find('.price-input').val().trim();
            let quantity = lastPriceRow.find('.quantity-input').val().trim();
            if (price || quantity) {
                addNewPriceRow();
                clearTimeout(autoSaveTimeout);
                autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
            } 
        // If there are no property rows, add one
        } else {
            addNewPriceRow();
        }
    });

    $(document).on('input change', '.product-info-input', function() {
        $(this).removeClass('error-input');
        let id = $(this).attr('id');
        $(`#${id}_error_field`).text('');
        checkForRemainingErrors();
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
    });

    $('#product-properties').sortable({
        start: function (e, ui) {
            ui.placeholder.css('margin-bottom', ui.item.css('margin-bottom'));
            ui.placeholder.css('margin-top', ui.item.css('margin-top'));
        }, 
        update: () => {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
        }
    });

    $('#images-inner-container').sortable({
        update: () => {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
        }
    });

    $('#cancel-changes-button').on('click', () => {
        fetch('/api/products/rollback_product_changes/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                'product_id': productId, 
                'initial_product_state_id': initialProductStateId
            })
        }).then(response => {
            if (response.ok) {
                // TODO - add redirection to whatever the previous page actually was
                location.href = `/admin_portal/`;
            } else {
                $('#extra-message-div').text('Error rolling back changes');
                setTimeout(() => {
                    $('#extra-message-div').text('');
                }, 2000);
                console.error('Error rolling back changes: ', response.json());
                
            }
        });
    });

    $('#upload-image-button').on('click', () => {
        if (!uploadInProgress) {
            $('#image-input').click();
        }
    });

    $('#image-input').on('change', function() {
        let imageFile = this.files[0];
        if (!imageFile) {
            return;
        }

        uploadInProgress = true;
        $('#upload-image-button').text('Uploading...');
        $('#upload-image-button').prop('disabled', true);
        $('#image-upload-progress').show();

        $('#inner-images-messages-label').text('');
        $('#inner-images-messages-label').hide();

        let formData = new FormData();
        formData.append('image', imageFile);
        formData.append('product_id', productId);

        $.ajax({
            url: '/api/products/add_image/',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: { 'X-CSRFToken': csrfToken },
            xhr: function() {
                let xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener('progress', (event) => {
                    if (event.lengthComputable) {            
                        let percentComplete = event.loaded / event.total * 100;
                        console.log(percentComplete);
                        $('#image-upload-progress').val(percentComplete);
                    }
                }, false);
                return xhr;
            },
            success: function(response) {
                if (response && response.url) {
                    console.log('Success');
                    addNewImageRow(response.url, response.id);
                    clearTimeout(autoSaveTimeout);
                    autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
                    $('#images-inner-container').sortable({
                        placeholder: 'sortable-placeholder',
                        start: function (e, ui) {
                            // Optionally adjust placeholder height to match dragged element
                            ui.placeholder.height(ui.item.outerHeight());
                            ui.placeholder.css('margin-bottom', ui.item.css('margin-bottom'));
                            ui.placeholder.css('margin-top', ui.item.css('margin-top'));
                            ui.item.siblings('.sortable-item').each(function () {
                                $(this).css({
                                    'margin-top': $(this).css('margin-top'),
                                    'margin-bottom': $(this).css('margin-bottom')
                                });
                            });
                        }
                    });
                } else {
                    console.error('Error uploading image: ', response);
                    // Show error message on page
                    $('#inner-images-messages-label').text('Error uploading image');
                    $('#inner-images-messages-label').addClass('error-message-div');
                    $('#inner-images-messages-label').show();
                }
            },
            error: function() {
                console.error('Error uploading image');
                $('#inner-images-messages-label').text('Error uploading image');
                $('#inner-images-messages-label').addClass('error-message-div');
                $('#inner-images-messages-label').show();
            },
            complete: function() {
                uploadInProgress = false;
                $('#upload-image-button').text('Upload Image');
                $('#upload-image-button').prop('disabled', false);
                $('#image-upload-progress').hide();
            }
        });
    });

    $('#cancel-changes-button').on('click', () => {
        rollBackProduct();
    });

    $('#remove-product-button').on('click', () => {
        $('#confirm-deletion-modal').modal('show');        
        $('#confirm-deletion-main-text').text('Are you sure you want to remove this product?');
        $('#confirm-deletion-button').on('click', () => {
            removeProduct();
        });
    });

    $('#save-product-button').on('click', () => {
        saveProductInfo();
    });
}

function showSavingIcon() {
    $('#product-saving-icon-container').show();
    $('#product-saved-icon-container').hide();
    $('#product-save-error-icon-container').hide();
}

function showSavedIcon() {
    $('#product-saved-icon-container').show();
    $('#product-saving-icon-container').hide();
    $('#product-save-error-icon-container').hide();
}

function showErrorIcon() {
    $('#product-save-error-icon-container').show();
    $('#product-saving-icon-container').hide();
    $('#product-saved-icon-container').hide();
}

function checkForRemainingErrors() {
    console.log('Checking for errors');
    if ($('.product-info-input.error-input').length == 0) {
        $('#product-save-error-icon-container').hide();
    }
}

function organizeFormData(data) {
    // Organize the form data into a dictionary, seperating properties into a sub-dictionary
    let organizedData = {};
    let properties = {};
    let prices = {};
    let imageIds = [];
    
    for (let entry of data.entries()) {
        let key = entry[0];
        let value = entry[1];
        if (key.includes('property-name')) {
            let propertyNumber = key.split('-')[2];
            let propertyName = value;
            let propertyValue = data.get(`property-value-${propertyNumber}`);
            properties[propertyName] = propertyValue;
        } else if (key.includes('price')) {
            let priceNumber = key.split('-')[1];
            let price = value;
            let quantity = data.get(`quantity-${priceNumber}`);
            prices[price] = quantity;
        } else if (key === 'image_id') {
            imageIds.push(value);
        } else if (!key.includes('property-value')) {
            organizedData[key] = value;
        } 
    }
    organizedData['properties'] = properties;
    organizedData['prices'] = prices;
    organizedData['image_ids'] = imageIds;
    return organizedData;
}

async function autoSaveProductForm(data) {
    // Send the form data to the server
    let organizedData = organizeFormData(data);

    console.log(organizedData);
    try {
        let response = await fetch('/api/products/autosave_product/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': organizedData.csrfmiddlewaretoken
            },
            body: JSON.stringify(organizedData)
        });

        return response;
        
    } catch (error) {
        console.log(error);
        showErrorIcon();
        return null;
    }
}

async function saveProductForm(data) {
    console.log(data);
    let organizedData = organizeFormData(data);
    console.log(organizedData);
    try {
        let response = await fetch('/api/products/final_save_product/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': organizedData.csrfmiddlewaretoken
            },
            body: JSON.stringify(organizedData)
        });

        return response;
    } catch (error) {
        console.log(error);
        showErrorIcon();
        return null;
    }
}

async function autoSaveProductInfo() {
    // Handle the auto-saving of the product form
    showSavingIcon();
    let readyToSubmit = true;

    if ($('#product_name').val().trim() == '') {
        readyToSubmit = false;
        $('#product_name').addClass('error-input');
    }

    $('.property-row').each(function () {
        let row = $(this);
        let propertyName = row.find('.property-name-input').val().trim();
        let propertyValue = row.find('.property-value-input').val().trim();
        
        if (!propertyName) {
            readyToSubmit = false;
            row.find('.property-name-input').addClass('error-input');
        }

        if (!propertyValue) {
            readyToSubmit = false;
            row.find('.property-value-input').addClass('error-input');
        } 
    });

    $('.price-row').each(function() {
        let row = $(this);
        let price = row.find('.price-input').val().trim();
        let quantity = row.find('.quantity-input').val().trim();

        if (!price) {
            readyToSubmit = false;
            row.find('.price-input').addClass('error-input');
        }

        if (!quantity) {
            readyToSubmit = false;
            row.find('.quantity-input').addClass('error-input');
        }
    });

    let formData = new FormData(document.getElementById('edit_product_form'));
    console.log(formData);

    if (readyToSubmit) {
        // Submit the form
        let response = await autoSaveProductForm(formData);
        if (response) {
            if (response.ok) {
                showSavedIcon();
            } else {
                showErrorIcon();
                let errorData = await response.json();
                console.error('Validation errors', errorData);
                Object.keys(errorData).forEach((field) => {
                    $(`#${field}`).addClass('error-input');
                    $(`#${field}_error_field`).text(errorData[field]);
                });
            }
        } else {
            // Unknown error
            showErrorIcon();
        }
    } else {
        showErrorIcon();
    }
}
async function rollBackProduct() {
    let response = await fetch('/api/products/rollback_product_changes/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            'product_id': productId, 
            'initial_product_state_id': initialProductStateId
        })
    });
    if (response.ok) {
        // TODO - add redirection to whatever the previous page actually was
        window.location.href = `/admin_portal/`;
    } else {
        $('#extra-message-div').removeClass('success-message-div');
        $('#extra-message-div').addClass('error-message-div');
        $('#extra-message-div').text('Error canceling changes');
        
        setTimeout(() => {
            $('#extra-message-div').text('');
        }, 2000);
        console.error('Error rolling back changes: ', response.json());
        
    }
}

async function removeProduct() {
    let response = await fetch(`/api/products/remove/${productId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
    });

    if (response.ok) {
        // TODO - add redirection to whatever the previous page actually was
        $('#confirm-deletion-main-text').removeClass('error-message-div');
        $('#confirm-deletion-main-text').addClass('deletion-success-message');
        $('#confirm-deletion-main-text').text('Product removed successfully');
        setTimeout(() => {
            $('#confirm-deletion-main-text').text('');
            window.location.href = `/admin_portal/`;
        }, 2000);
        
    } else {
        $('#confirm-deletion-main-text').removeClass('deletion-success-message');
        $('#confirm-deletion-main-text').addClass('error-message-div');
        $('#confirm-deletion-main-text').text('Error removing product');
        
        setTimeout(() => {
            $('#confirm-deletion-main-text').text('');
        }, 2000);
        console.error('Error removing product: ', response.json());
    }
}
async function saveProductInfo() {
    let readyToSave = true;
    if ($('#product_name').val().trim() == '') {
        $('#product_name').addClass('error-input');
        $('#product_name_error_field').text('Product name is required');
        readyToSave = false;
    }

    if (!$('#subcategory').val()) {
        $('#subcategory').addClass('error-input');
        $('#subcategory_error_field').text('Subcategory is required');
        readyToSave = false;
    }
    
    $('.property-row').each(function() {
        let row = $(this);
        let propertyName = row.find('.property-name-input').val().trim();
        let propertyValue = row.find('.property-value-input').val().trim();
        
        if (!propertyName) {
            row.find('.property-name-input').addClass('error-input');
            row.find('.property-name_error_field').text('Property name is required');
            readyToSave = false;
        }

        if (!propertyValue) {
            row.find('.property-value-input').addClass('error-input');
            row.find('.property-value_error_field').text('Property value is required');
            readyToSave = false;
        }
    });

    if (readyToSave) {
        let formData = new FormData(document.getElementById('edit_product_form'));
        let response = await saveProductForm(formData);
        console.log(response);
        console.log('Testing..');
        if (response) {
            if (response.ok) {
                $('#extra-message-div').text('Product saved successfully');
                $('#extra-message-div').removeClass('error-message-div');
                $('#extra-message-div').addClass('success-message-div');
                setTimeout(() => {
                    // TODO - add redirection to view product page
                    window.location.href = `/admin_portal/`;
                }, 2000);
            } else {
                let errorData = await response.json();
                console.error('Validation errors', errorData);
                Object.keys(errorData).forEach((field) => {
                    $(`#${field}`).addClass('error-input');
                    $(`#${field}_error_field`).text(errorData[field]);
                });
            }
        } else {
            $('#extra-message-div').text('Error saving product');
            $('#extra-message-div').removeClass('success-message-div');
            $('#extra-message-div').addClass('error-message-div');
            setTimeout(() => {
                $('#extra-message-div').text('');
            }, 2000);
        }
    }
}


function bindPropertyRemovalButtons() {
    $('.remove-property-button').on('click', function() {
        $(this).closest('.sortable-item').remove();
        checkForRemainingErrors();
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
    });
}

function bindPriceRemovalButtons() {
    $('.remove-price-button').on('click', function() {
        $(this).closest('.sortable-item').remove();
        checkForRemainingErrors();
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
    });
}
$(document).ready(() => {
    loadData();
    loadListeners();

    // This is necessary to bind the removal buttons that are already present on the page at load time
    bindPropertyRemovalButtons();
    bindPriceRemovalButtons();

    $('#product-properties').sortable({
        placeholder: 'sortable-placeholder',
        start: function (e, ui) {
            ui.placeholder.height(ui.item.outerHeight());
            ui.placeholder.css('margin-bottom', ui.item.css('margin-bottom'));
            ui.placeholder.css('margin-top', ui.item.css('margin-top'));
            ui.item.siblings('.sortable-item').each(function () {
                $(this).css({
                    'margin-top': $(this).css('margin-top'),
                    'margin-bottom': $(this).css('margin-bottom')
                });
            });
        }
    });
    $('#product-prices').sortable({
        placeholder: 'sortable-price-placeholder',
        start: function (e, ui) {
            console.log(ui.item.outerHeight());
            ui.placeholder.height(ui.item.outerHeight());
            ui.placeholder.css('margin-bottom', ui.item.css('margin-bottom'));
            ui.placeholder.css('margin-top', ui.item.css('margin-top'));
            ui.item.siblings('.sortable-item').each(function () {
                $(this).css({
                    'margin-top': $(this).css('margin-top'),
                    'margin-bottom': $(this).css('margin-bottom')
                });
            });
        }
    });    
});