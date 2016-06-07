/**
 * Created by Alexandre on 31/03/2016.
 */

// Date picker

jQuery(function($){
    $('.datepicker').datepicker({
        dateFormat : 'dd/mm/yy'
    });
});

// Autocompletion username
jQuery(function($){
    $('.autocomplete_username').autocomplete({
        source: function( request, response ) {
            $.ajax({
                url: "/users/user/api/unpr/",
                dataType: "json",
                data: {
                    search: request.term
                },
                success: function( data ) {
                    alert(data);
                    response( data );
                }
            });
        }
    });
});

