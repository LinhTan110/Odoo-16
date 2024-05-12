odoo.define('my_online_appointment.main', function (require) {
    "use strict";

    $(document).ready(function(){
        $('.description-content').each(function(){
            if ($(this).height() > 100) {
                $(this).addClass('show-less');
            }
        });

        $('.read-more-btn').click(function(){
            var descriptionContent = $(this).prev('.description-content');
            descriptionContent.toggleClass('show-less');
            if (descriptionContent.hasClass('show-less')) {
                $(this).text('Xem thêm');
            } else {
                $(this).text('Thu gọn');
            }
            $('.read-more-btn').toggle($('.description-content.show-less').length > 0);
        });
    });
});
