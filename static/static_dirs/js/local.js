/*
   Our local JS file
*/

// Adapt Body padding bottom to footer's height
var adaptBodyPaddingToFooter = function() {
	if ($(".footer").length > 0) {
		height = $(".footer").height();
		$('body').css("padding-bottom",height);
	}
}
jQuery(function($){
  adaptBodyPaddingToFooter();
  
  $(window).resize(function() {
	  adaptBodyPaddingToFooter();
  })
})

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
