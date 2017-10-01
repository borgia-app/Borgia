/*
   Our local JS file
*/

jQuery(function($){
  if ($(".notification .notification-actor").length > 0) {
     $(".notification .notification-actor").each(function() {
           var link=$(this).attr("data-link");
           $(this).click(function() {
               window.location.replace(link);
           });
     });
  }
})
