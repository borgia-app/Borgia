/*
   Our local JS file
*/

// Adapt Body padding bottom to footer's height
var adaptBodyPaddingToFooter = function() {
	if ($(".footer").length > 0) {
		height = $(".footer").height();
		$('body').css("padding-bottom",height);

		if ($(".content").length > 0) {
			content_height = $(".content").height();
			if ( content_height < $(window).height() ) {
				$('.footer').css("position","fixed");
			} else {
				$('.footer').css("position","absolute");
			}
		}
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
