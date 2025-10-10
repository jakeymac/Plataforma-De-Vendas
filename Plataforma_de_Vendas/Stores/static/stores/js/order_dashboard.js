let currentPage = 1;

function buildQueryParms() {
    // Build query parameters for the API request
    let searchQuery = $("#order-search-input").val();
    let filterValue = $("#order-filter-selector").val();
    let sortValue = $("#order-sort-selector").val();

    let params = new URLSearchParams();
    params.append('page', currentPage);
    if (searchQuery) {
        params.append('search', searchQuery);
    }
    if (filterValue) {
        params.append('filters', JSON.stringify({'status': filterValue}));
    }
    if (sortValue) {
        params.append('sort', sortValue);
    }
    return params;
}

function buildOrderRow(order) {
    // Build a table row for an order to be inserted into the table body
    let date = new Date(order.created_at);
    let options = { month: 'short', day: '2-digit', year: 'numeric' };
    let formattedDate = date.toLocaleDateString('en-US', options).replace(',', '').replace(' ', '-');
    let row = `
    <tr>
        <td>${order.id}</td>
        <td>${order.user_username}</td>
        <td>${order.user_first_name} ${order.user_last_name}</td>
        <td>${formattedDate}</td>
        <td>$${order.total}</td>
        <td>${order.status}</td>
        <td class="text-center"><a href="/orders/${order.id}/" class="btn btn-primary btn-sm">View</a></td>
    </tr>`;

    return row;
}

function loadOrders() {
    // Fetch orders and populate the table
    let params = buildQueryParms();
    fetch(`/api/orders/search/?${params}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log("Data received: ", data);
        
        $("#orders-table-body").empty();
        data.orders.forEach(order => {
            let row = buildOrderRow(order); 
            $("#orders-table-body").append(row);
        });
        $("#total-orders-count").text(`Total: ${data.order_count}`);
        $("#page-number").text(`Page ${currentPage} of ${data.page_count}`);
        if (currentPage > 1) {
            $("#prev-page-button").prop("disabled", false);
            
        } else {
            $("#prev-page-button").prop("disabled", true);
        }

        if (currentPage < data.page_count) {
            $("#next-page-button").prop("disabled", false);
        } else {
            $("#next-page-button").prop("disabled", true);
        }
        
        if (data.order_count == 0) {
            let noDataRow = `<tr><td colspan="6" class="text-center">No orders found.</td></tr>`;
            $("#orders-table-body").append(noDataRow);
        }
    })
}

function loadListeners() {
    // Load event listeners
    $("#refresh-button").on("click", function() {
        currentPage = 1;
        loadOrders();
    });

    $("#order-search-input").on("input", function() {
        let value = $(this).val();
        if (value.length > 0) {
            $("#clear-search-button").removeClass("d-none");
        } else {
            $("#clear-search-button").addClass("d-none");
        }
    })

    $("#order-search-input").on("keypress", function(e) {
    if (e.which === 13) { // Enter key
        currentPage = 1;
        loadOrders();
    }
});

    $("#clear-search-button").on("click", function() {
        $("#order-search-input").val("");
        $(this).addClass("d-none");
        currentPage = 1;
        loadOrders();
    });

    $("#search-button").on("click", function() {
        currentPage = 1;
        loadOrders();
    });

    $(".update-selector").on("change", function() {
        currentPage = 1;
        loadOrders();
    });   

    $("#prev-page-button").on("click", function() {
        currentPage --;
        loadOrders();
    });

    $("#next-page-button").on("click", function() {
        currentPage ++;
        loadOrders();
    });
}

$(document).ready(function() {
    // Initial Load
    loadOrders();
    loadListeners();
    
});