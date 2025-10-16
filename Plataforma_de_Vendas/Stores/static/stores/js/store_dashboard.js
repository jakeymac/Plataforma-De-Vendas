
function buildOrderRow(order) {
    // Build a table row for an order object
    let date = new Date(order.created_at);
    let options = { month: 'short', day: '2-digit', year: 'numeric' };
    let formattedDate = date.toLocaleDateString('en-US', options).replace(',', '').replace(' ', '-');
    let row = `<tr>
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

function loadRecentOrders() {
    // Fetch recent orders and populate the table
    let params = new URLSearchParams();
    params.append('filters', JSON.stringify({'store': storeId}));
    params.append('sort', 'newest');

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
        console.log('Recent orders data received: ', data);

        $('#recent-orders-table-body').empty();
        data.orders.forEach(order => {
            let row = buildOrderRow(order); 
            $('#recent-orders-table-body').append(row);
        });
    });
}

function loadListeners() {
    $('#refresh-orders-button').click(() => {
        loadRecentOrders();
    });
}

$(document).ready(() => {
    loadRecentOrders();
    loadListeners();

});