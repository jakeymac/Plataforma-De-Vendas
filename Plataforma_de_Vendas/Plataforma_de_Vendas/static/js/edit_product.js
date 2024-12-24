// Debounce timer for auto-saving
// TODO make sure auto save isn't on while images are uploading

let autoSaveTimeout;
let uploadInProgress = false;

function addNewPropertyRow() {
    $("#sortable-properties").append(`
        <div class="row sortable-item property-row" id="property-row-${counter}">
            <div class="col-md-5">
                <label for="property-name-${counter}">Property Name</label>
                <input type="text" class="form-control product-info-input property-name-input" id="property-name-${counter}" name="property-name-${counter}">
            </div>
            <div class="col-md-5">
                <label for="property-value-${counter}">Property Value</label>
                <input type="text" class="form-control product-info-input property-value-input" id="property-value-${counter}" name="property-value-${counter}">
            </div>
            <div class="col-md-2">
                <button type="button" class="btn btn-danger remove-property-button">Remove</button>
            </div>
            <div class="col-md-12">
                <div class="error-message-div" id=""></div>
                <div class="error-message-div"></div>
            </div>
        </div>`);
    counter++;
    bindRemovalButtons();
}

function addNewImageRow(imageUrl, imageId, isInitial=false) {
    let newPhotoRow = `<div class="row photo-row">
                            <div class="col-12 photo-row-inner-container sortable-item">
                                <div class="col-6" id="product-image-${imageId}-container">
                                    <img src="${imageUrl}" alt="Product Image" class="product-image">
                                </div>
                                <div class="col-6 remove-image-button-container">
                                    <button type="button" class="btn btn-danger remove-image-button" id="remove-image-${imageId}">Remove Image</button>
                                </div>
                                <input type="hidden" name="image_id" id="image_id" value="${imageId}">
                            </div>
                        </div>`;
    $("#photos-inner-container").append(newPhotoRow); 
    if (!isInitial) {
        $(".photo-row").show();
    }   
    $(`#remove-image-${imageId}`).on("click", function() {
        let imageId = $(this).closest(".photo-row").find("#image_id").val();
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
                $(this).closest(".photo-row").remove();
                clearTimeout(autoSaveTimeout);
                autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
            } else {
                console.error("Error removing image: ", response.json());
                // TODO add error message to page
            }
        });
    })
}

function loadData() {
    // Load the product images
    $("#initial-image-loading-icon-container").show();
    fetch(`/api/products/images/${productId}/`)
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            console.error("Error loading images: ", response.json());
            // TODO add error message to page
            $("#initial-image-loading-icon-container").hide();
        } 
    })
    .then(data => {
        if (data.images && data.images.length > 0) {
            let images = data.images;
            let imagesLoaded = 0;
            var totalImages = images.length;

            if (!images) {
                $("#initial-image-loading-icon-container").hide();
            }

            for (let image of images) {
                addNewImageRow(image.url, image.id, true);
                // TODO look into fixing this, if there are any issues with loading, no images will be shown
                $(`#product-image-${image.id}-container img`).on("load", function () {
                    imagesLoaded++;
                    console.log(imagesLoaded);
                    if (imagesLoaded === totalImages) {
                        $("#initial-image-loading-icon-container").hide();
                        $(".photo-row").show();   
                        $("#photos-inner-container").sortable({
                            placeholder: "sortable-placeholder",
                            start: function (e, ui) {
                                // Optionally adjust placeholder height to match dragged element
                                ui.placeholder.height(ui.item.outerHeight());
                                ui.placeholder.css("margin-bottom", ui.item.css("margin-bottom"));
                                ui.placeholder.css("margin-top", ui.item.css("margin-top"));
                                ui.item.siblings(".sortable-item").each(function () {
                                    $(this).css({
                                        "margin-top": $(this).css("margin-top"),
                                        "margin-bottom": $(this).css("margin-bottom")
                                    });
                                });
                            }
                        })
                    }
                });
            }
            $("#initial-image-loading-icon-container").hide();
        }
        $("#initial-image-loading-icon-container").hide();

    })
    .catch(error => {
        console.error("Error loading images: ", error);
        // TODO add error message to page
        $("#initial-image-loading-icon-container").hide();
    })


}

function loadListeners() {
    $("#add-property-button").on("click", function() {
        // Grab the last property row in the form and check if it has values, otherwise don't add a new row
        let lastPropertyRow = $("#sortable-properties .sortable-item:last");
        if (lastPropertyRow.length > 0) {
            let propertyName = lastPropertyRow.find(".property-name-input").val().trim();
            let propertyValue = lastPropertyRow.find(".property-value-input").val().trim();
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

    $(document).on("input change", ".product-info-input", function() {
        $(this).removeClass("error-input");
        let id = $(this).attr('id');
        $(`#${id}_error_field`).text("");
        checkForRemainingErrors();
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
    })

    $("#sortable-properties").sortable({
        start: function (e, ui) {
            ui.placeholder.css("margin-bottom", ui.item.css("margin-bottom"));
            ui.placeholder.css("margin-top", ui.item.css("margin-top"));
        }, 
        update: function (event, ui) {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
        }
    })

    $("#photos-inner-container").sortable({
        update: function (event, ui) {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
        }
    });

    $("#cancel-changes-button").on("click", function() {
        fetch('/api/products/rollback_product_changes/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({"product_id": productId, 
                                  "initial_product_state_id": initialProductStateId})
        }).then(response => {
            if (response.ok) {
                // TODO - add redirection to whatever the previous page actually was
                location.href = `/admin_portal/`;
            } else {
                $("#extra-error-message-div").text("Error rolling back changes");
                setTimeout(() => {
                    $("#extra-error-message-div").text("");
                }, 2000);
                console.error("Error rolling back changes: ", response.json());
                
            }
        });
    })

    $("#upload-image-button").on("click", function() {
        if (!uploadInProgress) {
            $("#image-input").click();
        }
    });

    $("#image-input").on("change", function() {
        let imageFile = this.files[0];
        if (!imageFile) {
            return;
        }

        uploadInProgress = true;
        $("#upload-image-button").text("Uploading...");
        $("#upload-image-button").prop("disabled", true);
        $("#image-upload-progress").show();

        let formData = new FormData();
        formData.append("image", imageFile);
        formData.append("product_id", productId);

        $.ajax({
            url: "/api/products/add_image/",
            method: "POST",
            data: formData,
            processData: false,
            contentType: false,
            headers: { "X-CSRFToken": csrfToken },
            xhr: function() {
                let xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener("progress", function(event) {
                    if (event.lengthComputable) {            
                        let percentComplete = event.loaded / event.total * 100;
                        console.log(percentComplete)
                        $("#image-upload-progress").val(percentComplete);
                    }
                }, false);
                return xhr;
            },
            success: function(response) {
                if (response && response.url) {
                    console.log("Success");
                    
                    addNewImageRow(response.url, response.id);
                    clearTimeout(autoSaveTimeout);
                    autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
                    $("#photos-inner-container").sortable({
                        placeholder: "sortable-placeholder",
                        start: function (e, ui) {
                            // Optionally adjust placeholder height to match dragged element
                            ui.placeholder.height(ui.item.outerHeight());
                            ui.placeholder.css("margin-bottom", ui.item.css("margin-bottom"));
                            ui.placeholder.css("margin-top", ui.item.css("margin-top"));
                            ui.item.siblings(".sortable-item").each(function () {
                                $(this).css({
                                    "margin-top": $(this).css("margin-top"),
                                    "margin-bottom": $(this).css("margin-bottom")
                                });
                            });
                        }
                    })
                    
                } else {
                    console.error("Error uploading image: ", response);
                    // Show error message on page
                }
            },
            error: function() {
                console.error("Error uploading image");
                // Show error message on page
            },
            complete: function() {
                uploadInProgress = false;
                $("#upload-image-button").text("Upload Image");
                $("#upload-image-button").prop("disabled", false);
                $("#image-upload-progress").hide();
            }
        });
    });

    
}

function showSavingIcon() {
    $("#product-saving-icon-container").show();
    $("#product-saved-icon-container").hide();
    $("#product-save-error-icon-container").hide();
}

function showSavedIcon() {
    $("#product-saved-icon-container").show();
    $("#product-saving-icon-container").hide();
    $("#product-save-error-icon-container").hide();
}

function showErrorIcon() {
    $("#product-save-error-icon-container").show();
    $("#product-saving-icon-container").hide();
    $("#product-saved-icon-container").hide();
}

function checkForRemainingErrors() {
    console.log("Checking for errors");
    if ($(".product-info-input.error-input").length == 0) {
        $("#product-save-error-icon-container").hide();
    }
}

function organizeFormData(data) {
    // Organize the form data into a dictionary, seperating properties into a sub-dictionary
    let organizedData = {};
    let properties = {};
    let imageIds = [];
    
    for (let entry of data.entries()) {
        let key = entry[0];
        let value = entry[1];
        if (key.includes("property-name")) {
            let propertyNumber = key.split("-")[2];
            let propertyName = value;
            let propertyValue = data.get(`property-value-${propertyNumber}`);
            properties[propertyName] = propertyValue;
        } else if (key === "image_id") {
            imageIds.push(value);
        } else if (!key.includes("property-value")) {
            organizedData[key] = value;
        } 
    }
    organizedData["properties"] = properties;
    organizedData["image_ids"] = imageIds;
    return organizedData;
}

async function saveProductForm(data) {
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

async function autoSaveProductInfo() {
    // Handle the auto-saving of the product form
    console.log("Saving...");
    showSavingIcon();
    let readyToSubmit = true;

    if ($("#product_name").val().trim() == "") {
        readyToSubmit = false;
        $("#product_name").addClass("error-input");
    }

    $(".property-row").each(function () {
        let row = $(this);
        let propertyName = row.find(".property-name-input").val().trim();
        let propertyValue = row.find(".property-value-input").val().trim();
        
        if (!propertyName) {
            readyToSubmit = false;
            row.find(".property-name-input").addClass("error-input");
        }

        if (!propertyValue) {
            readyToSubmit = false;
            row.find(".property-value-input").addClass("error-input");
        } 
    })

    let formData = new FormData(document.getElementById("edit_product_form"));
    console.log(formData);

    if (readyToSubmit) {
        // Submit the form
        let response = await saveProductForm(formData);
        if (response) {
            if (response.ok) {
                showSavedIcon();
            } else {
                showErrorIcon();
                let errorData = await response.json();
                console.error("Validation errors", errorData);
                Object.keys(errorData).forEach(function(field) {
                    $(`#${field}`).addClass("error-input");
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

function bindRemovalButtons() {
    $(".remove-property-button").on("click", function() {
        
        $(this).closest(".sortable-item").remove();
        checkForRemainingErrors();
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
    })
}
$(document).ready(function() {
    loadData();
    loadListeners();
    bindRemovalButtons(); // This is necessary to bind the removal buttons that are already present on the page at load time
    $("#sortable-properties").sortable({
        placeholder: "sortable-placeholder",
        start: function (e, ui) {
            // Optionally adjust placeholder height to match dragged element
            ui.placeholder.height(ui.item.outerHeight());
            ui.placeholder.css("margin-bottom", ui.item.css("margin-bottom"));
            ui.placeholder.css("margin-top", ui.item.css("margin-top"));
            ui.item.siblings(".sortable-item").each(function () {
                $(this).css({
                    "margin-top": $(this).css("margin-top"),
                    "margin-bottom": $(this).css("margin-bottom")
                });
            });
        }
    });    
});