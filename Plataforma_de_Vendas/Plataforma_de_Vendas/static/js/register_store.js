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
        $("store-registration-container").hide();
        $("#account-registration-container").show();
    });

    $("#next-button").on("click", function() {
        var found_errors = false;
        if ($("#username").val().trim() === "") {
            var inputField = $("#username");
            var errorDiv = $("#username-error-div");
            errorDiv.text("Username is required");
            inputField.addClass('is-invalid');
            errorDiv.show();
            found_errors = true;
        } else {
            fetch('/api/accounts/username_available', {
                method: 'POST',
                body: JSON.stringify({ username: $("#username").val() }),
                headers: {
                    'Content-Type': 'application/json', 
                }
            })
            .then(response => {
                if (!response.is_available) {
                    var inputField = $("#username");
                    var errorDiv = $("#username-error-div");
                    errorDiv.text("Username is already taken");
                    inputField.addClass('is-invalid');
                    errorDiv.show();
                    found_errors = true;
                }
            })
            .catch(error => {
                console.log(error);
            });
        }
        
        if ($("#email").val().trim() === "") {
            var inputField = $("#email");
            var errorDiv = $("#email-error-div");
            errorDiv.text("Email is required");
            inputField.addClass('is-invalid');
            errorDiv.show();
            found_errors = true;
        } else {
            fetch('/api/accounts/email_available', {
                method: 'POST',
                body: JSON.stringify({ email: $("#email").val() }),
                headers: {
                    'Content-Type': 'application/json', 
                }
            })
            .then(response => {
                if (!response.is_available) {
                    var inputField = $("#email");
                    var errorDiv = $("#email-error-div");
                    errorDiv.text("Email is already taken");
                    inputField.addClass('is-invalid');
                    errorDiv.show();
                    found_errors = true;
                }
            })
            .catch(error => {
                console.log(error);
            });
        }
        
        if ($("#password").val().length < 8) {
            passwordField = $("#password");
            passwordErrorDiv = $("#password-error-div");
            passwordErrorDiv.text("Password must be at least 8 characters long");
            passwordField.addClass('is-invalid');
            passwordErrorDiv.show();
            found_errors = true;
        }
        if ($("#first_name").val().trim() === "") {
            var inputField = $("#first_name");
            var errorDiv = $("#first_name-error-div");
            errorDiv.text("First name is required");
            inputField.addClass('is-invalid');
            errorDiv.show();
            found_errors = true;
        }

        if ($("#last_name").val().trim() === "") {
            var inputField = $("#last_name");
            var errorDiv = $("#last_name-error-div");
            errorDiv.text("Last name is required");
            inputField.addClass('is-invalid');
            errorDiv.show();
            found_errors = true;
        }

        if (!found_errors) {
            $("#account-registration-container").hide();   
            $("#store-registration-container").show(); 
        }
   });


    $('input').on('input', function() {
        var inputField = $(this);
        var errorDiv = inputField.next('.invalid-feedback');
        inputField.removeClass('is-invalid').next('.invalid-feedback').empty().hide();
    });

    $("#store-registration-form").submit(function(event) {
        event.preventDefault();
        var accountData= {};
        var storeData = {};
        
        $("#account-registration-container input").each(function() {
            var name=$(this).attr('name');
            var value = $(this).val();
            accountData[name] = value;
        });

        $("#store-registration-container input").each(function() {
            var name=$(this).attr('name');
            var value = $(this).val();
            storeData[name] = value;
        });

        console.log("Account info: ", accountData);
        console.log("Store Info: ", storeData);
    });
}

$(document).ready(function() {
    load_event_listeners();
})