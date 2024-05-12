odoo.define('my_online_appointment.datlich', function (require) {
    "use strict";
    var ajax = require('web.ajax');

    $(document).ready(function () {
        var selectedTable = null;
        var buttonNext = document.getElementById('button_next');
        var buttonSearch = document.getElementById('button_search');

        if (buttonNext) {
            buttonNext.addEventListener("click", handleCreateAppointment);
        }
        if (buttonSearch) {
            buttonSearch.addEventListener("click", handleSearchTables);
        }

        function handleCreateAppointment(event) {
            event.preventDefault();
//            if (!selectedTable) {
//                alert('Please select a table before proceeding.');
//                return;
//            }
            var formData = collectFormData();
            ajax.jsonRpc('/create_appointment', 'http', formData)
                .then(function (result) {
                    if (result.error) {
                        alert(result.error);
                    } else {
                        window.location.href = '/success';
                    }
                })
                .catch(function (error) {
                    console.error('Error:', error);
                    alert('An error occurred. Please try again.');
                });
        }

        function handleSearchTables(event) {
            event.preventDefault();
            var formData = {
                'capacity': document.getElementById('capacity').value,
                'location_table': document.getElementById('location_table').value,
                'characteristic': document.getElementById('characteristic').value,
                'start': document.getElementById('start').value,
                'duration': document.getElementById('duration').value,
                'allday': document.getElementById('allday').checked,
            };
            ajax.jsonRpc('/search_tables', 'json', formData)
                .then(function (result) {
                    const container = $('#buttons_container');
                    container.empty(); // Clear previous buttons
                    if (result.available_tables && result.available_tables.length > 0) {
                        container.show(); // Show container when there are tables
                        result.available_tables.forEach(table => {
                            const button = $('<button>')
                                .text('Table' + table.name)
                                .addClass('table-button')
                                .on('click', function(event) {
                                    event.preventDefault();
                                    $('.table-button').removeClass('selected'); // Reset các nút khác
                                    $(this).addClass('selected'); // Nổi bật nút này
                                    selectedTable = table.id;
                                });
                            container.append(button);
                        });
                    } else {
                        container.hide(); // Hide container if no tables found
                        container.append('<div>No available tables found.</div>');
                    }
                })
                .catch(function (error) {
                    console.error('Error:', error);
                    alert('An error occurred during search. Please try again.');
                });
        }

        function collectFormData() {
            return {
                'name': document.getElementById('name').value,
                'phone': document.getElementById('phone').value,
                'email': document.getElementById('email').value,
                'restaurant_name': document.getElementById('restaurant_name').value,
                'address': document.getElementById('address').value,
                'note': document.getElementById('note').value,
                'start': document.getElementById('start').value,
                'duration': document.getElementById('duration').value,
                'allday': document.getElementById('allday').checked,
                'capacity': document.getElementById('capacity').value,
                'location_table': document.getElementById('location_table').value,
                'characteristic': document.getElementById('characteristic').value,
                'formattedDate': formattedDate(document.getElementById('start').value),
//                'table_id': selectedTable,
            };
        }

        function formattedDate(start) {
            var startDate = new Date(start);
            return startDate.getFullYear() + '-' + ('0' + (startDate.getMonth() + 1)).slice(-2) + '-' + ('0' + startDate.getDate()).slice(-2);
        }
    });
    $(document).ready(function(){
        var now = new Date();
        var formattedDate = formattedDateOnly(now);
        var formattedDateTime = formatDate(now);
        $('#start').val(formattedDateTime);
        $('#start').change(function() {
            var selectedDate = new Date($(this).val());
            formattedDateTime = formatDate(selectedDate);
            formattedDate = formattedDateOnly(selectedDate);
        });
        $('#allday').change(function() {
            var allDayCheckbox = $(this);
            var durationInput = $('#duration');
            var startDateInput = $('#start');
            if (allDayCheckbox.is(':checked')) {
                durationInput.prop('disabled', true);
                startDateInput.attr('type', 'date'); // Chỉ hiển thị ngày
                startDateInput.val(formattedDate); // Hiển thị ngày đã chọn
            } else {
                durationInput.prop('disabled', false);
                startDateInput.attr('type', 'datetime-local'); // Hiển thị ngày và giờ
                startDateInput.val(formattedDateTime); // Hiển thị ngày và giờ đã chọn
            }
        });
    });
    function formattedDateOnly(date) {
        var year = date.getFullYear();
        var month = ('0' + (date.getMonth() + 1)).slice(-2);
        var day = ('0' + date.getDate()).slice(-2);
        var formattedDate = year + '-' + month + '-' + day;
        return formattedDate;
    }
    function formatDate(datetime) {
        var date = new Date(datetime);
        var year = date.getFullYear();
        var month = ('0' + (date.getMonth() + 1)).slice(-2);
        var day = ('0' + date.getDate()).slice(-2);
        var hours = ('0' + date.getHours()).slice(-2);
        var minutes = ('0' + date.getMinutes()).slice(-2);
        var formattedDateTime = year + '-' + month + '-' + day + 'T' + hours + ':' + minutes;
        return formattedDateTime;
    }
});