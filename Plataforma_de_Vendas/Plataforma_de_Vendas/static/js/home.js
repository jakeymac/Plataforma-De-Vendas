$(document).ready(function() {
    fetch('api/products/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Error in request');
        }
    })
    .then(data => {
        console.log(data);
    });
});