$(function(){
  $("#id_allow_self_registeration").change(function() {
    if (this.checked) {
        $("#id_date_end_registration").prop('disabled', false);
    } else {
	    $("#id_date_end_registration").prop('disabled', true);
	}
  });
});