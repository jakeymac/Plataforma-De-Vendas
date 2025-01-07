function load_event_listeners() {
    $("#home-nav-button").on("click", function() {
        window.location.href = "/";
        console.log("Clicked home button");
    });

    $("#admin-account-nav-button").on("click", function() {
        window.location.href = "/admin_account";
    });

    $("#customer-account-nav-button").on("click", function() {
        window.location.href = "/customer_account";
    });

    $("#my-store-nav-button").on("click", function() {
        window.location.href = "/my_store";
    });

    $("#login-nav-button").on("click", function() {
        window.location.href = "/login";
    });

    $("#register-account-nav-button").on("click", function() {
        window.location.href = "/register_account";
    });

    $("#register-seller-nav-button").on("click", function() {
        window.location.href = "/register_seller";
    });

    $("#logout-nav-button").on("click", function() {
        window.location.href = "/logout";
    });
}


$(document).ready(function() {
    load_event_listeners();
});