function loadEventListeners() {
    $("#profile-picture-input").change(function() {
        uploadProfilePicture();
    });

    $("#edit-account-information-button").click(function() {
        changeToEditMode();
    })

    $(".edit-field").on("input", function() {
        $(this).removeClass('is-invalid');
        $(`#${this.id}_error_div`).empty().hide();
    });

    $("#edit_country_phone_number_code").on("change", function() {
        $("#edit_phone_number").removeClass('is-invalid');
        $("#phone_number_error_div").empty().hide();
    });

    $("#cancel-edit-account-information-button").click(function() {
        $("#account-information-edit-container").hide();
        $("#account-information-display-container").show();
        
    });
    $("#edit-account-information-form").submit(function(event) {
        event.preventDefault();
        var formData = new FormData(this);
        formData.append('id', userId);

        fetch("/api/accounts/edit_user/", {
            method: 'PUT',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === "User updated") {
                location.reload();  // Reload the page
            } else {
                console.log(data);
                if (data.errors) {
                    for (var key in data.errors) {
                        $(`#edit_${key}`).addClass('is-invalid');
                        $(`#${key}_error_div`).text(data.errors[key]).show();
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating the account information.');
        });

      
    });
}

function uploadProfilePicture() {
    var fileInput = document.getElementById('profile-picture-input');
    var formData = new FormData();
    formData.append('profile_picture', fileInput.files[0]);
    formData.append('id', userId);

    fetch("/api/accounts/update_profile_picture/", {
        method: 'PUT',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Profile picture updated") {
            location.reload();  // Reload the page to show the new profile picture
        } else {
            alert(data.message);  // Handle any errors
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while uploading the profile picture.');
    });
}

function changeToEditMode() {
    $("#account-information-display-container").hide();
    $("#account-information-edit-container").show()
}

$(document).ready(function() {
    loadEventListeners();
});