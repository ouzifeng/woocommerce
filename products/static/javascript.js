$(document).ready(function() {
    // Toggle visibility of columns based on user preferences
    $(".column-toggle").change(function() {
        const columnName = $(this).val();
        if ($(this).is(":checked")) {
            $(`.${columnName}`).show();
        } else {
            $(`.${columnName}`).hide();
        }
    });

    // Save column preferences via AJAX
    $('#saveColumnPrefs').on('click', function() {
        const preferences = [];
        $('.column-toggle').each(function() {
            preferences.push({
                column_name: $(this).attr('id'),
                is_visible: $(this).is(':checked')
            });
        });

        $.ajax({
            url: '/save_column_prefs/',
            method: 'POST',
            data: {
                csrfmiddlewaretoken: '{{ csrf_token }}',
                preferences: JSON.stringify(preferences)
            },
            success: function(response) {
                if (response.success) {
                    alert('Preferences saved successfully!');
                } else {
                    alert('Error saving preferences.');
                }
            },
            error: function() {
                alert('Error saving preferences due to a network issue.');
            }
        });
    });

    // Handle progress modal for various buttons
    function showProgressModal(button, message) {
        $('#progressModal').modal('show');
        $('#progressText').text(message);
        setTimeout(function() {
            window.location.href = $(button).attr('href');
        }, 500);
    }

    $("#importButton").click(function(e) {
        e.preventDefault();
        showProgressModal(this, "Importing products, please wait...");
    });

    $("#resyncButton").click(function(e) {
        e.preventDefault();
        showProgressModal(this, "Resyncing products, please wait...");
    });

    // Fetch live product data and update the product table
    const productIds = new Set();
    $(".col-product_id").each(function() {
        const productId = parseInt($(this).text().trim());
        if (!isNaN(productId)) {
            productIds.add(productId);
        }
    });

    $.ajax({
        url: '/fetch-live-product-data/',
        data: {
            'product_ids': [...productIds].join(',')
        },
        success: function(response) {
            const discrepantProductIds = [];
            for (const productId in response) {
                const data = response[productId];
                if (updateTableData(productId, 'regular_price', data.regular_price) ||
                    updateTableData(productId, 'sale_price', data.sale_price) ||
                    updateTableData(productId, 'stock_quantity', data.stock_quantity)) {
                        
                    discrepantProductIds.push(productId);
                }
            }

            if (discrepantProductIds.length > 0) {
                $.ajax({
                    url: '/update-products/',
                    type: 'POST',
                    data: {
                        'product_ids': discrepantProductIds.join(','),
                        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                    },
                    success: function(response) {
                        // Handle success here if needed
                    },
                    error: function() {
                        alert('Error updating products due to a network issue.');
                    }
                });
            }
        },
        error: function() {
            alert('Error fetching live product data due to a network issue.');
        }
    });

    function updateTableData(productId, type, apiValue) {
        const currentElem = $(`td[data-product-id='${productId}'][data-product-type='${type}']`);
        const currentValue = parseFloat(currentElem.text());

        if (currentValue !== parseFloat(apiValue)) {
            currentElem.text(apiValue);
            return true;  // Indicating there was a discrepancy
        }
        return false;
    }
});
