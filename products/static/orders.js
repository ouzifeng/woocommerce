document.addEventListener("DOMContentLoaded", function() {
    // Extract order IDs from the displayed table
    let orderIds = Array.from(document.querySelectorAll(".order-row[data-order-id]"))
        .map(row => row.getAttribute('data-order-id'));

    // Make an AJAX request to fetch live order data
    fetch(`/orders/fetch_live_data/?order_ids=${orderIds.join(",")}`)
        .then(response => response.json())
        .then(data => {
            // Update the displayed order statuses based on the live data
            for (let order of orderIds) {
                let liveStatus = data[order]?.status;
                if (liveStatus) {
                    // Find the table row for this order using the data-attribute
                    let row = document.querySelector(`tbody .order-row[data-order-id="${order}"]`);
                    // Update the status cell
                    row.querySelector("td:nth-child(2)").textContent = liveStatus;
                }
            }
        });
});
