// Dict to use for form fetch calls
const apiUrls = {'add-category-form': '/api/products/categories/add', 
              'add-subcategory-form': '/api/products/subcategories/add',
              'edit-category-form': '/api/products/categories/update',
              'edit-subcategory-form': '/api/products/subcategories/update'};

const deleteButtons = {'category': 'categories', 'subcategory': 'subcategories'};

function load_data() {

}
  
function load_listeners() {
    $(".form-control").focus(function (){
        $(this).removeClass('error-input');
        $(`#${$(this).attr('id')}_error_container`).text("");
    })

    // TODO add a listener to the selecters to remove the error message when the user selects a value


    $(".delete-button").click(async function () {
        const buttonId = $(this).attr('id');
        // Remove the delete- prefix and -button suffix
        const cleanedButtonId = buttonId.replace(/^delete-/, '').replace(/-button$/, '');
        
        const targetId = $(`#edit_${cleanedButtonId}_selector`).val();
        const url = `/api/products/${deleteButtons[cleanedButtonId]}/remove/${targetId}`;
        if (targetId === "") {
            $(`#edit-${cleanedButtonId}-error-container`).text("Please select a category to delete");
            return;
        }

        try {
            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.log(errorData);
            } else {
                window.location.reload();
            }
        } catch (error) {
            alert("Network error: " + error.message);
        }
    });

    $("form").submit(async function (e) {
        e.preventDefault();
        const formData = new FormData(this);
        const formId = $(this).attr('id');
        const formUrl = apiUrls[formId];
        var method;
        if (formId.includes('edit')) {
            method = 'PUT';
        } else {
            method = 'POST';
        }
        try {
            const response = await fetch(formUrl, {
                method: method,
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData 
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.log(errorData);
                for (var field in errorData) {
                    if (formId.includes('edit')) {
                        $(`#edit_${field}_error_container`).text(errorData[field]);
                        $(`#edit_${field}`).addClass('error-input'); 
                    } else {
                        $(`#${field}_error_container`).text(errorData[field]);
                        $(`#${field}`).addClass('error-input');
                    }
                }
            } else {
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


