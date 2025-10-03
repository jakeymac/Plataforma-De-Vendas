function load_listeners() {
    $('#add_new_product_form').submit( async function (e) {
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
                    $('#messages-container').text(errorData.message);
                    $('#messages-container').addClass('alert alert-danger');
                    $('#product_name').addClass('error-input');
                }
            } else {
                let responseData = await response.json();
                $(this).closest('form').find('#messages-container').text('Success');
                $(this).closest('form').find('#messages-container').addClass('alert alert-success');    
                let productId = responseData.id;
                setTimeout(() => {
                    window.location.href = `/edit_product/${productId}`;
                }, 2000);
            }
        } catch(error) {
            $(this).closest('form').find('#messages-container').text('Error: ' + error.message);
            $(this).closest('form').find('#messages-container').addClass('alert alert-danger');
        }
    });

    $('#product_name').on('input', () => {
        $('#product_name').removeClass('error-input');
        $('#messages-container').text('');
        $('#messages-container').removeClass('alert alert-danger');
    });
}
$(document).ready(() => {
    load_listeners();
});