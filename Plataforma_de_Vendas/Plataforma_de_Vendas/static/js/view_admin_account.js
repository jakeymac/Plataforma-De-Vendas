function load_event_listeners() {

}

function load_data() {
    fetch('/api/accounts/current_user/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
        }
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Error in request');
        }
    })
    .then(data => {
        console.log(data);
        if (data.username) {
            $('#username-label').text(`Username: ${data.username}`);
        } else {
            $('#username-label').text('No username found');
        }

        if (data.email) {
            $('#email-label').text(`Email: ${data.email}`);
        } else {
            $('#email-label').text('No email found');
        }

        if (data.first_name) {
            $('#first-name-label').text(`First name: ${data.first_name}`);
        } else {
            $('#first-name-label').text('No first name found');
        }

        if (data.last_name) {
            $('#last-name-label').text(`Last name: ${data.last_name}`);
        } else {
            $('#last-name-label').text('No last name found');
        }

        
    }); 
}

$(document).ready(() => {
    load_event_listeners();
    load_data();
});