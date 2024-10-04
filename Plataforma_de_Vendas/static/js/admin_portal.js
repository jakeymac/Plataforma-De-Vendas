function load_data() {

}
  
function load_listeners() {
    $("#add-category-form").submit(async function (e) {
        e.preventDefault();

        const form_data = new FormData(this); 

        try {
            const response = await fetch('/api/products/categories/add', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: form_data 
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.log(errorData);
                for (var field in errorData) {
                    $(`#${field}_error_container`).text(errorData[field]);
                }
                alert("Error: " + (errorData.message || "Something went wrong"));
            } else {
                const data = await response.json();
                window.location.reload();
            }
        } catch (error) {
            alert("Network error: " + error.message);
        }
    });
}

$(document).ready(function () {
    load_data();
    load_listeners();
});


