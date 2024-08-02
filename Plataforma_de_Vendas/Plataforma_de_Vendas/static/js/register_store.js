function load_event_listeners() {
    document.getElementById('profile_picture').addEventListener('change', function() {
        var fileNameSpan = document.querySelector('label[for="' + this.id + '"] span');
        var fileName = this.files.length > 0 ? this.files[0].name : 'Choose file...';
        fileNameSpan.textContent = fileName;
    });
    document.getElementById('store_logo').addEventListener('change', function() {
        var fileNameSpan = document.querySelector('label[for="' + this.id + '"] span');
        var fileName = this.files.length > 0 ? this.files[0].name : 'Choose file...';
        fileNameSpan.textContent = fileName;
    });

   $("#back-home-button").on("click", function() {
        window.location.href = "/";
   })

   $("#back-user-registration-button").on("click", function() {
        var found_errors = false;
        fetch('/api/accounts/username_available', {
            method: 'POST',
            body: JSON.stringify({ username: $("#username").val() }),
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                response.json().then(data => {
                    var inputField = $("#username");
                    var errorDiv = $("#username-error-div");
                    errorDiv.text("That username is taken");
                    inputField.addClass('is-invalid');
                    errorDiv.show();
                    found_errors = true;
                });
            }
        })

        if (!found_errors) {
            $("#store-registration-container").hide();
            $("#account-registration-container").show();    
        }
   });

   $("#next-button").on("click", function() {
        $("#account-registration-container").hide();
        $("#store-registration-container").show();
   });

    $('input').on('input', function() {
        var inputField = $(this);
        var errorDiv = inputField.next('.invalid-feedback');
        inputField.removeClass('is-invalid').next('.invalid-feedback').empty().hide();
    });

    $("#store-registration-form").submit(function(event) {
        event.preventDefault();
        var form_data = new FormData(this);
        fetch('/api/stores/register', { 
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
                alert('Store created');
                window.location.href = "/login";
            }
            
        });
    });
}

$(document).ready(function() {
    load_event_listeners();
})