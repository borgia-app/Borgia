$(function(){

  function get_total_price () {
    return $("#id_update_form-price").val();
  };

  function get_total_ponderation () {
    var total_ponderation = 0
    $("[id^='ponderation_']").each(function() {
      var id = $(this).attr('id').split('_')[1]
      total_ponderation += Number($('#ponderation_' + id).val())
    });
    return total_ponderation;
  };

  function set_prices () {
    var total_price = get_total_price();
    if ( total_price ){
      var total_ponderation = get_total_ponderation();
      var price_per_ponderation = total_price / total_ponderation;

      $("[id^='ponderation_']").each(function() {
        var id = $(this).attr('id').split('_')[1];
        var ponderation = $(this).val();
        var r_price = Math.round( Number(ponderation * price_per_ponderation * 100) ) / 100;
        $("#price_" + id).text(r_price + '€');
      });
    }
    else {
      $("[id^='ponderation_']").each(function() {
        $("#price_" + id).text("Indéfini");
      });
    }
  };


  $(set_prices());
  $("[id^='ponderation_']").change(function() {
    set_prices();
  });
  $("#id_update_form-price").change(function() {
    set_prices();
  });
});
