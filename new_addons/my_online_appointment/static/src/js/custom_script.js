odoo.define('my_module.custom_script', function (require) {
    'use strict';

    var ajax = require('web.ajax');

    $(document).ready(function() {
        // On change event for the country dropdown
        $('#country_id').on('change', function() {
            var countryId = $(this).val();

            // Make an AJAX request to retrieve the tables based on the selected country
            ajax.jsonRpc('/get_tables', 'call', {'country_id': countryId})
                .then(function (tables) {
                    // Clear existing options
                    $('#table_id').empty();

                    // Add new options based on the retrieved tables
                    $.each(tables, function(index, table) {
                        $('#table_id').append($('<option>', {
                            value: table.id,
                            text: table.name
                        }));
                    });
                });
        });
    });
});
