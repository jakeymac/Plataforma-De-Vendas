function load_event_listeners() {
    document.getElementById('profile_picture').addEventListener('change', function() {
        var fileNameSpan = document.querySelector('label[for="' + this.id + '"] span');
        var fileName = this.files.length > 0 ? this.files[0].name : 'Choose file...';
        fileNameSpan.textContent = fileName;
    });

    $("#back-button").on("click", function() {
        window.location.href = "/";
    });

    $('input').on('input', function() {
        var inputField = $(this);
        var errorDiv = inputField.next('.invalid-feedback');
        inputField.removeClass('is-invalid').next('.invalid-feedback').empty().hide();
    });

    $("#account-registration-form").submit(function(event) {
        event.preventDefault();
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