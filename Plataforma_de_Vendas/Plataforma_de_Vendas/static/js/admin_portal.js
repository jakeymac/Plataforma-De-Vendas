// Dict to use for form fetch calls
const apiUrls = {'add-category-form': '/api/products/categories/add/', 
                 'add-subcategory-form': '/api/products/subcategories/add/',
                 'edit-category-form': '/api/products/categories/update/',
                 'edit-subcategory-form': '/api/products/subcategories/update/',
                 'top-categories-form': '/api/products/topsubcategories/update/'};

const deleteButtons = {'category': 'categories', 'subcategory': 'subcategories'};


function update_product_selector(products) {
    $("#edit-product-selector").empty();
    if (products.length === 0) {
        $("#edit-product-selector").append('<option value="">No products found</option>');
    } else {
        $("#edit-product-selector").append('<option value="">Select a product</option>');
        products.forEach(product => {
            $("#edit-product-selector ").append(`<option value="${product.id}">${product.product_name}</option>`);
        });
    }
}

function load_listeners() {
    $(".form-control").on("input", function () {
        const inputId = $(this).attr("id");
        // Remove error class and clear error message
        $(`#${inputId}`).removeClass("error-input");
        $(`#${inputId}_error_container`).text("");
    });

    $(".form-select").on("change", function () {
        const selectId = $(this).attr("id");
        // Remove error class and clear error message
        $(`#${selectId}`).removeClass("error-input");
        $(`#${selectId}_error_container`).text("");
    });

    $(".delete-button").click(async function () {
        const buttonId = $(this).attr('id');
        // Remove the delete- prefix and -button suffix
        const cleanedButtonId = buttonId.replace(/^delete-/, '').replace(/-button$/, '');
        
        const targetId = $(`#edit_${cleanedButtonId}_selector`).val();
        const url = `/api/products/${deleteButtons[cleanedButtonId]}/remove/${targetId}/`;
        if (targetId === "") {
            $(`#edit-${cleanedButtonId}-error-container`).text("Please select a category to delete");
            return;
        }
        try {
            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });
            if (!response.ok) {
                const errorData = await response.json();
                console.log(errorData);
            } else {
                $(this).closest("form").find(".message-container").text("Success");
                $(this).closest("form").find(".message-container").addClass("success-message");
                setTimeout(function() {
                    window.location.reload();
                }, 2000);
            }
        } catch (error) {
            alert("Network error: " + error.message);
        }
    });

    $("form").submit(async function (e) {
        e.preventDefault();
        const formData = new FormData(this);
        const formId = $(this).attr('id');
        const formUrl = apiUrls[formId];
        var method;
        if (formId.includes('edit')) {
            method = 'PUT';
        } else {
            method = 'POST';
        }
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
                        $("#top-categories-message-container").text(errorData.error);
                        $("#top-categories-message-container").addClass("error-message");
                    }
                }            
            } else {
                $(this).find(".message-container").text("Success");
                $(this).find(".message-container").addClass("success-message");
                setTimeout(function() {
                    window.location.reload();
                }, 2000);
            }
        } catch (error) {
            $(this).find(".message-container").text("Error: " + error.message);
            $(this).find(".message-container").addClass("error-message");
        }
    }); 
    
    $("#edit-product-button").on("click", function() {
        let productId = $("#edit-product-selector").val();
        if (productId == "") {
            $("#edit-product-message-container").removeClass("error-message");
            $("#edit-product-message-container").text("Please select a product to edit");
        } else {
            // Check for product's existence to avoid errors
            fetch(`/api/products/${productId}/`,
            {
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => {
                if (!response.ok) {
                    if (response.status === 404) {
                        $("#edit-product-message-container").addClass("error-message");
                        $("#edit-product-message-container").text("Product not found");
                    } else {
                        $("#edit-product-message-container").addClass("error-message");
                        $("#edit-product-message-container").text("An error occurred");
                    }
                } else {
                    window.location.href = '/edit_product/' + productId;
                }
            })
        }
    });
    
    $("#edit_category_selector").change(function () {
        let category = categories.find(cat=> cat.id == $(this).val()); // Uses the categories object pulled from the context in a script in the template
        $("#edit_category_name").val(category.category_name);
        $("#edit_category_description").val(category.category_description);
    });

    $("#edit_subcategory_selector").change(function() {
        let subcategory = subcategories.find(subcat=> subcat.id == $(this).val()); // Uses the subcategories object pulled from the context in a script in the template
        $("#edit_subcategory_name").val(subcategory.subcategory_name);
        $("#edit_subcategory_description").val(subcategory.subcategory_description);
        $("#edit_subcategory_category_selector").val(subcategory.category_id);
    });

    $("#product-search").on("input", function () {
        let searchTerm = $(this).val();
        let filteredProducts = products.filter(product => {
            return product.product_name.toLowerCase().includes(searchTerm) || (product.product_description && product.product_description.toLowerCase().includes(searchTerm));
        });
        update_product_selector(filteredProducts);
    })
}

$(document).ready(function () {
    load_listeners();
});


