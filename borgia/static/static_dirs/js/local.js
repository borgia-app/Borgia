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
			footerHeight = $(".footer").height();
			if ( contentHeight + footerHeight < $(window).height() ) {
				$('body').css("padding-bottom",$(window).height() - contentHeight)
			}
		}
	}
}
// Adapt sidebar height to content
var adaptSidebarHeight = function(wh) {
	if (( $("#sidebar").length > 0 ) && ( $(window).width() < 768 ) ) {
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