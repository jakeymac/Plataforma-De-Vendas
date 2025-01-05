const $homeButton = $("#home-nav-button");
const $adminAccountButton = $("#admin-account-nav-button");
const $customerAccountButton = $("#customer-account-nav-button");
const $myStoreButton = $("#my-store-nav-button");
const $loginButton = $("#login-nav-button");
const $registerAccountButton = $("#register-account-nav-button");
const $registerSellerButton = $("#register-seller-nav-button");
const $logoutButton = $("#logout-nav-button");

function load_event_listeners() {
    $homeButton.on("click", function() {
        window.location.href = "/";
        console.log("Clicked home button");
    });

    $adminAccountButton.on("click", function() {
        window.location.href = "/admin_account";
    });

    $customerAccountButton.on("click", function() {
        window.location.href = "/customer_account";
    });

    $myStoreButton.on("click", function() {
        window.location.href = "/my_store";
    });

    $loginButton.on("click", function() {
        window.location.href = "/login";
    });

    $registerAccountButton.on("click", function() {
        window.location.href = "/register_account";
    });

    $registerSellerButton.on("click", function() {
        window.location.href = "/register_seller";
    });

    $logoutButton.on("click", function() {
        window.location.href = "/logout";
    });
}


$(document).ready(function() {
    load_event_listeners();
});