function load_user_registration_listeners() {
    $("#profile_picture").on("change", function() {
        var fileNameSpan = $('label[for="' + this.id + '"] span');
        var fileName = this.files.length > 0 ? this.files[0].name : 'Choose file...';
        fileNameSpan.text(fileName);
    });

    $("#back-home-button").on("click", function() {
        window.location.href = "/";
   });

   $("#next-button").on("click", async function() {
    var foundErrors = false;

    if ($("#username").val().trim() === "") {
        var inputField = $("#username");
        var errorDiv = $("#username-error-div");
        errorDiv.text("Username is required");
        inputField.addClass('is-invalid');
        errorDiv.show();
        foundErrors = true;
    } else {
        try {
            const response = await fetch('/api/accounts/username_available', {
                method: 'POST',
                body: JSON.stringify({ "username": $("#username").val() }),
                headers: {
                    'Content-Type': 'application/json', 
                    'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() 
                }
            });
            const data = await response.json();
            if (!data.is_available) {
                var inputField = $("#username");
                var errorDiv = $("#username-error-div");
                errorDiv.text("Username is already taken");
                inputField.addClass('is-invalid');
                errorDiv.show();
                foundErrors = true;
            }
        } catch (error) {
            console.log(error);
        }
    }
    

    if ($("#email").val().trim() === "") {
        var inputField = $("#email");
        var errorDiv = $("#email-error-div");
        errorDiv.text("Email is required");
        inputField.addClass('is-invalid');
        errorDiv.show();
        foundErrors = true;
    } else {
        try {
            const response = await fetch('/api/accounts/email_available', {
                method: 'POST',
                body: JSON.stringify({ "email": $("#email").val() }),
                headers: {
                    'Content-Type': 'application/json', 
                    'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() 
                }
            });
            const data = await response.json();
            if (!data.is_available) {
                var inputField = $("#email");
                var errorDiv = $("#email-error-div");
                errorDiv.text("Email is already taken");
                inputField.addClass('is-invalid');
                errorDiv.show();
                foundErrors = true;
            }
            
        } catch (error) {
            console.log(error);
        }
    }
    
    if ($("#password").val().length < 8) {
        passwordField = $("#password");
        passwordErrorDiv = $("#password-error-div");
        passwordErrorDiv.text("Password must be at least 8 characters long");
        passwordField.addClass('is-invalid');
        passwordErrorDiv.show();
        foundErrors = true;
    }
    if ($("#first_name").val().trim() === "") {
        var inputField = $("#first_name");
        var errorDiv = $("#first_name-error-div");
        errorDiv.text("First name is required");
        inputField.addClass('is-invalid');
        errorDiv.show();
        foundErrors = true;
    }

    if ($("#last_name").val().trim() === "") {
        var inputField = $("#last_name");
        var errorDiv = $("#last_name-error-div");
        errorDiv.text("Last name is required");
        inputField.addClass('is-invalid');
        errorDiv.show();
        foundErrors = true;
    }

    if (!foundErrors) {
        $("#account-registration-container").hide();   
        $("#store-registration-container").show();
    }
    });
}

function load_store_registration_listeners() {
    $("#store_logo").on("change", function() {
        var fileNameSpan = $('label[for="' + this.id + '"] span');
        var fileName = this.files.length > 0 ? this.files[0].name : 'Choose file...';
        fileNameSpan.text(fileName);
    });

    $("#back-user-registration-button").on("click", function() {
        $("#store-registration-container").hide();
        $("#account-registration-container").show();
    });

    $("#store-registration-form").submit(function(event) {
        event.preventDefault();
    
        var foundErrors = false;
        
        if ($("#store_name").val().trim() === "") {
            var inputField = $("#store_name");
            var errorDiv = $("#store_name-error-div");
            errorDiv.text("Store name is required");
            inputField.addClass('is-invalid');
            errorDiv.show();
            foundErrors = true;
        }
    
        if ($("#store_description").val().trim() === "") {
            var inputField = $("#store_description");
            var errorDiv = $("#store_description-error-div");
            errorDiv.text("Store description is required");
            inputField.addClass('is-invalid');
            errorDiv.show();
            foundErrors = true;
        }

        if ($("#contact_email").val().trim() === "") {
            var inputField = $("#contact_email");
            var errorDiv = $("#contact_email-error-div");
            errorDiv.text("Contact email is required");
            inputField.addClass('is-invalid');
            errorDiv.show();
            foundErrors = true;
        }
        
        if ($("#store_url").val().trim() === "") {
            var inputField = $("#store_url");
            var errorDiv = $("#store-url-error-div");
            errorDiv.text("Store URL is required");
            inputField.addClass('is-invalid');
            errorDiv.show();
        }

        if (!foundErrors) {
            var accountData= {};
            var storeData = {};
            
            var formData = new FormData(this);
            
            fetch('/api/stores/register/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
                }
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
                    console.log(data);
                    if (data.message == "Store created successfully") {
                        window.location.href = "/login";
                    } else {
                        if (data.message == "Server Error") {
                            alert("There was an error, try again in a moment");
                        } else {
                            alert('Store not created');
                            if (data.errors.account_errors) {
                                Object.keys(data.errors.account_errors).forEach(key => {
                                    var inputField = $(`#${key}`);
                                    var errorDiv = $(`#${key}-error-div`);
                                    errorDiv.text(data.errors.account_errors[key]);
                                    inputField.addClass('is-invalid');
                                    errorDiv.show();
                                });
                                $("#store-registration-container").hide();
                                $("#account-registration-container").show();
                            }
                            if (data.errors.store_errors) {
                                Object.keys(data.errors.store_errors).forEach(key => {
                                    var inputField = $(`#${key}`);
                                    var errorDiv = $(`#${key}-error-div`);
                                    errorDiv.text(data.errors.store_errors[key]);
                                    inputField.addClass('is-invalid');
                                    errorDiv.show();
                                });
                            }
                        }
                    }
                }
            })
            .catch(error => {
                console.log(error);
            });
        }
    });
}

function load_event_listeners() {
    $('input').on('input', function() {
        var inputField = $(this);
        var errorDiv = inputField.next('.invalid-feedback');
        inputField.removeClass('is-invalid').next('.invalid-feedback').empty().hide();
    });
}

$(document).ready(function() {
    load_event_listeners();
    load_user_registration_listeners();
    load_store_registration_listeners();
})