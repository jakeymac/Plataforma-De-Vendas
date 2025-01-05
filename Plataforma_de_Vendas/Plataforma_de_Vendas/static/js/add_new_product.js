const $addNewProductForm = $("#add_new_product_form");
const $productNameInput = $("#product_name");
const $messagesContainer = $("#messages-container");
function load_listeners() {
    $addNewProductForm.submit( async function (e) {
        e.preventDefault();
        const formData = new FormData(this);
        
        try {
            let response = await fetch('/api/products/add/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData
            });

            if (!response.ok) {
                let errorData = await response.json();
                if (errorData.message) {
                    $messagesContainer.text(errorData.message);
                    $messagesContainer.addClass("error-message");
                    $productNameInput.addClass('error-input');
                }
            } else {
                let responseData = await response.json();
                $(this).closest("form").find("#messages-container").text("Success");
                $(this).closest("form").find("#messages-container").addClass("success-message");    
                let productId = responseData.id;
                setTimeout(function() {
                    window.location.href = `/edit_product/${productId}`;
                }, 2000);
            }
        } catch(error) {
            $(this).closest("form").find("#messages-container").text("Error: " + error.message);
            $(this).closest("form").find("#messages-container").addClass("error-message");
        }
    });

    $productNameInput.on("input", function() {
        $productNameInput.removeClass('error-input');
        $messagesContainer.text("");
        $messagesContainer.removeClass("error-message");
    })
}
$(document).ready(function() {
    load_listeners();
});