// Date picker
jQuery(function($) {
  $('.datepicker').datepicker({
    format: 'dd/mm/yyyy',
    language: 'fr'
  })
})

// Autocompletion username
jQuery(function($) {
  $('.autocomplete_username').autocomplete({
    source: function(request, response) {
      $.ajax({
        url: '/ajax/username_from_username_part/',
        dataType: 'json',
        data: {
          keywords: request.term
        },
        success: function(data) {
          response(data)
        }
      })
    }
  })
})
