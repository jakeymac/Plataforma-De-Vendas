function load_event_listeners() {
    $("#login-form").submit(function(event) {
        event.preventDefault();
        var form_data = new FormData(this);
        fetch('/api/accounts/login', {
            method: 'POST',
            body: form_data
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                response.json().then(data => {
                    $("#login-error-div").text(data.message).show();
                });
            }
        })
        .then(data => {
            if (data.message == "Logged in") {
                window.location.href = "/home";
            }
        });
    });
}

$(document).ready(function() {
    load_event_listeners();
});