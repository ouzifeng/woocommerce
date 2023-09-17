$(document).ready(function () {
    $(".column-toggle").change(function () {
        let columnName = $(this).val();
        if ($(this).is(":checked")) {
            // show column
            $(`.${columnName}`).show();
        } else {
            // hide column
            $(`.${columnName}`).hide();
        }
    });
});


$('#saveColumnPrefs').on('click', function () {
    let preferences = [];
    $('.column-toggle').each(function () {
        preferences.push({
            column_name: $(this).attr('id'),
            is_visible: $(this).is(':checked')
        });
    });

    $.ajax({
        url: '/save_column_prefs/',  // The URL endpoint you'll create in Django views.
        method: 'POST',
        data: {
            csrfmiddlewaretoken: '{{ csrf_token }}',
            preferences: JSON.stringify(preferences)
        },
        success: function (response) {
            if (response.success) {
                alert('Preferences saved successfully!');
            } else {
                alert('Error saving preferences.');
            }
        }
    });
});


// This function should be in the global scope
function updateProgress() {
    $.get('/get-progress/', function(data) {
        $('#progressText').text(data.progress);
        
        // You can set a condition to hide the modal when the progress reaches 100 or any completion criteria.
        if(data.progress === "Finished") {
            $('#progressModal').modal('hide');
        } else {
            setTimeout(updateProgress, 2000);  // Check again after 2 seconds
        }
    });
}

$(document).ready(function() {
    // For importing products
    $("#importButton").click(function(e) {
        e.preventDefault();
        
        // Show the modal indicating the process is ongoing
        $('#progressModal').modal('show');
        $('#progressText').text("Importing products, please wait...");

        // Navigate to the actual import URL after a short delay
        setTimeout(function() {
            window.location.href = $("#importButton").attr('href');
        }, 500);
    });

    // For resyncing products
    $("#resyncButton").click(function(e) {
        e.preventDefault();
        
        // Show the modal indicating the process is ongoing
        $('#progressModal').modal('show');
        $('#progressText').text("Resyncing products, please wait...");

        // Navigate to the actual resync URL after a short delay
        setTimeout(function() {
            window.location.href = $("#resyncButton").attr('href');
        }, 500);
    });
});


$(document).ready(function() {
    var productIds = [];
    
    $(".col-product_id").each(function() {
        var productId = parseInt($(this).text().trim());
        if (!isNaN(productId) && productIds.indexOf(productId) === -1) {
            productIds.push(productId);
        }
    });

    $.ajax({
        url: '/fetch-live-product-data/',
        data: {
            'product_ids': productIds.join(',')
        },
        success: function(response) {
            var discrepantProductIds = [];
            
            for (var productId in response) {
                var data = response[productId];
                
                if (updateTableData(productId, 'regular_price', data.regular_price) ||
                    updateTableData(productId, 'sale_price', data.sale_price) ||
                    updateTableData(productId, 'stock_quantity', data.stock_quantity)) {
                        
                    discrepantProductIds.push(productId);
                }
            }

            if (discrepantProductIds.length > 0) {
                // Now, inside this if block, make the AJAX call to `/update-products/`
                $.ajax({
                    url: '/update-products/',
                    type: 'POST',
                    data: {
                        'product_ids': discrepantProductIds.join(','),
                        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                    },
                    success: function(response) {
                        // Handle success here if needed
                    }
                });
            }
        }
    });
});

function updateTableData(productId, type, apiValue) {
    var currentElem = $(`td[data-product-id='${productId}'][data-product-type='${type}']`);
    var currentValue = parseFloat(currentElem.text());

    if (currentValue !== parseFloat(apiValue)) {
        currentElem.text(apiValue);
        return true;  // Indicating there was a discrepancy
    }
    return false;
}
