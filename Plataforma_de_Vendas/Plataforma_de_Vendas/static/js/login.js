function load_event_listeners() {
    $("#login-button").on("click", function() {
        fetch('/api/accounts/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
            },
            body: JSON.stringify({
                username: $("#username-input").val(),
                password: $("#password-input").val(),
            })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Error in request');
            }
        })
        .then(data => {
            if (data.message == "Logged in") {
                window.location.href = "/home";
            } else {
                
            }
            
        });
    });
}

$(document).ready(function() {
    load_event_listeners();
});