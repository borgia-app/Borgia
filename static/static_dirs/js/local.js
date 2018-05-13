/*
   Our local JS file
*/

// Adapt Body padding bottom to footer's height
var adaptBodyPaddingToFooter = function() {
	if ($(".footer").length > 0) {
		height = $(".footer").height();
		$('body').css("padding-bottom",height);

		if ($(".content").length > 0) {
			contentHeight = $(".content").height();
			if ( contentHeight < $(window).height() ) {
				$('.footer').css("position","fixed");
			} else {
				$('.footer').css("position","absolute");
			}
		}
	}
}
// Adapt sidebar height to content
var adaptSidebarHeight = function(wh) {
	if (( $("#sidebar").length > 0 )) {
			$('#sidebar').height(wh);
			$('#sidebar .mp-level').height($('#sidebar').prop('scrollHeight'));
	}
}
jQuery(function($){
  adaptBodyPaddingToFooter();
  adaptSidebarHeight($(window).height());
  
  $(window).resize(function() {
	  adaptBodyPaddingToFooter();
	  adaptSidebarHeight($(window).height());
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
