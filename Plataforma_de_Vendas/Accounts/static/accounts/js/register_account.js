function load_event_listeners() {
    $('#profile_picture').on('change', function() {
        var fileNameSpan = $('label[for="' + this.id + '"] span');
        var fileName = this.files.length > 0 ? this.files[0].name : 'Choose file...';
        fileNameSpan.text(fileName);
    });

    $('#back-button').on('click', () => {
        window.location.href = '/';
    });

    $('input').on('input', function() {
        var inputField = $(this);
        inputField.removeClass('is-invalid').next('.invalid-feedback').empty().hide();
    });

    $('#test-button').on('click', () => {
        $('#registration-confirmation-modal').modal('show');
    });

    $('#account-registration-form').submit(function(event) {
        event.preventDefault();
        var form_data = new FormData(this);
        form_data.append('account_type', 'customer');
        fetch('/api/accounts/register/', { 
            method: 'POST',
            body: form_data
        })
        .then(response => {
            if (response.status === 201) {
                console.log('Success');
                return response.json();

            } else {
                console.log('Error');
                response.json().then(data => {
                    Object.keys(data).forEach(key => {
                        var inputField = $(`#${key}`);
                        var errorDiv = $(`#${key}-error-div`);
                        errorDiv.text(data[key]);
                        inputField.addClass('is-invalid');
                        errorDiv.show();
                    });
                });
                console.log(response);
            }
        })
        .then(() => {
            $('#registration-confirmation-main-text').text('Your account has been registered');
            $('#registration-confirmation-main-text').addClass('alert alert-success');
            $('#registration-confirmation-modal').modal('show');
            $('#registration-confirmation-modal-continue-button').on('click', () => {
                window.location.href = '/login';
            });
            
        });
    });
}

$(document).ready(() => {
    load_event_listeners();
});