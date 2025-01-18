function load_event_listeners() {
    $("#profile_picture").on("change", function() {
        var fileNameSpan = $('label[for="' + this.id + '"] span');
        var fileName = this.files.length > 0 ? this.files[0].name : 'Choose file...';
        fileNameSpan.text(fileName);
    });

    $("#back-button").on("click", function() {
        window.location.href = "/";
    });

    $('input').on('input', function() {
        var inputField = $(this);
        var errorDiv = inputField.next('.invalid-feedback');
        inputField.removeClass('is-invalid').next('.invalid-feedback').empty().hide();
    });

    $("#test-button").on("click", function() {
        $("#registration-confirmation-modal").modal('show');
    });

    $("#account-registration-form").submit(function(event) {
        event.preventDefault();
        $("#registration-confirmation-modal").modal('show');
        var form_data = new FormData(this);
        form_data.append("account_type", "customer");
        fetch('/api/accounts/register/', { 
            method: 'POST',
            body: form_data
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                response.json().then(data => {
                    Object.keys(data).forEach(key => {
                        var inputField = $(`#${key}`);
                        var errorDiv = $(`#${key}-error-div`);
                        errorDiv.text(data[key]);
                        inputField.addClass('is-invalid');
                        errorDiv.show();
                    })
                });
                console.log(response);
            }
        })
        .then(data => {
            if (data) {
                window.location.href = "/login";
            }
            
        });
    });
}

$(document).ready(function() {
    load_event_listeners();
});