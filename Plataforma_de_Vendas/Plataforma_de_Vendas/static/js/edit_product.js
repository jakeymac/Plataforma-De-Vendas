function loadListeners() {
    $("#add-property-button").on("click", function() {
        console.log("Pressed add");
        $("#sortable-properties").append(`
            <div class="row sortable-item" id="property-row-${counter}">
                <div class="col-md-5">
                    <label for="property-name-${counter}">Property Name</label>
                    <input type="text" class="form-control" id="property-name-${counter}" name="property-name-${counter}">
                </div>
                <div class="col-md-5">
                    <label for="property-value-${counter}">Property Value</label>
                    <input type="text" class="form-control" id="property-value-${counter}" name="property-value-${counter}">
                </div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-danger remove-property-button">Remove</button>
                </div>
            </div>`);
        counter++;
        bindRemovalButtons();
    });
    
    $(".form-control").on("change", function() {
        console.log("Changed");

    });
    
}

function bindRemovalButtons() {
    $(".remove-property-button").on("click", function() {
        console.log("Pressed remove");
        $(this).closest(".form-row").remove();
    })
}
$(document).ready(function() {
    loadListeners();
    bindRemovalButtons(); // This is necessary to bind the removal buttons that are already present on the page at load time
    $("#sortable-properties").sortable({
        placeholder: "sortable-placeholder",
        start: function (e, ui) {
            // Optionally adjust placeholder height to match dragged element
            ui.placeholder.height(ui.item.outerHeight());
        }
    });
});