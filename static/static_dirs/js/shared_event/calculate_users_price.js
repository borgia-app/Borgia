$(function(){

  function get_total_price () {
    return $("#id_update_form-price").val();
  };

  function get_total_weight () {
    var total_weight = 0
    $("[id^='weight_']").each(function() {
      total_weight += Number($(this).val())
    });
    return total_weight;
  };

  function set_prices () {
    var total_price = get_total_price();
    if ( total_price ){
      var total_weight = get_total_weight();
      var price_per_weight = total_price / total_weight;

      $("[id^='weight_']").each(function() {
        var id = $(this).attr('id').split('_')[2];
        var weight = $(this).val();
        var r_price = Math.round( Number(weight) * price_per_weight * 100 ) / 100;
        $("#price_" + id).text(r_price + '€');
      });
    }
    else {
      $("[id^='weight_']").each(function() {
        $("#price_" + id).text("Indéfini");
      });
    }
  };


  $(set_prices());
  $("[id^='weight_']").change(function() {
    set_prices();
  });
  $("#id_update_form-price").change(function() {
    set_prices();
  });
});
