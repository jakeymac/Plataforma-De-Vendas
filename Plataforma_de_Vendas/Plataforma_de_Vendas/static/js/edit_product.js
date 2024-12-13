// Debounce timer for auto-saving
let autoSaveTimeout;

function addNewPropertyRow() {
    $("#sortable-properties").append(`
        <div class="row sortable-item" id="property-row-${counter}">
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
        update: function (event, ui) {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(autoSaveProductInfo, 1500);
        }
    })

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
    for (let entry of data.entries()) {
        let key = entry[0];
        let value = entry[1];
        if (key.includes("property-name")) {
            let propertyNumber = key.split("-")[2];
            let propertyName = value;
            let propertyValue = data.get(`property-value-${propertyNumber}`);
            properties[propertyName] = propertyValue;
        } else if (!key.includes("property-value")) {
            organizedData[key] = value;
        }
    }
    organizedData["properties"] = properties;
    return organizedData;
}

async function saveProductForm(data) {
    // Send the form data to the server
    let organizedData = organizeFormData(data);

    console.log(organizedData);
    try {
        let response = await fetch('/api/products/update/', {
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

    $(".sortable-item").each(function () {
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
    })
}
$(document).ready(function() {
    loadListeners();
    bindRemovalButtons(); // This is necessary to bind the removal buttons that are already present on the page at load time
    $("#sortable-properties").sortable({
        placeholder: "sortable-placeholder",
        start: function (e, ui) {
            // Optionally adjust placeholder height to match dragged element
            ui.placeholder.height(ui.item.outerHeight());
        }
    });
});