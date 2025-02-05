function load_event_listeners() {
    $('input').on('input', () => {
        $('#login-error-div').empty().hide();
    });

    $('#login-form').submit(function(event) {
        event.preventDefault();
        var form_data = new FormData(this);
        fetch('/api/accounts/login/', {
            method: 'POST',
            body: form_data
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                response.json().then(data => {
                    $('#login-error-div').text(data.message).show();
                });
            }
        })
        .then(data => {
            if (data.message) {
                if (data.message == 'Logged in') {
                    var next_link = $('#next-link').val();
                    if (next_link) {
                        if (next_link[0] != '/') {
                            next_link = '/' + next_link;
                        }
                        window.location.href = next_link;
                    } else {
                        window.location.href = '/home';
                    }
                } else {
                    $('#login-error-div').text(data.message).show();
                }
            } else {
                $('#login-error-div').text('An error occurred').show();
            }
            
        });
    });

    $('#register-button').click(() => {
        window.location.href = '/register';
    });
}

$(document).ready(() => {
    load_event_listeners();
});