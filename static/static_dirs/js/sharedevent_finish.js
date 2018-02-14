$(showTotalPrice()); // On laod

$("#id_type_payment").change(function(){ // On change
  var selected = $("#id_type_payment option:selected").val();
  switch (selected) {
    case "pay_by_total":
      showTotalPrice();
      break;
    case "pay_by_ponderation":
      showPonderationPrice();
      break;
    case "no_payment":
      hideBoth();
      break;
    }
});

function showTotalPrice() {
  // On load
  $( ".form-group" ).eq(1).show();
  $( ".form-group" ).eq(2).hide();
}

function showPonderationPrice() {
  // On load
  $( ".form-group" ).eq(1).hide();
  $( ".form-group" ).eq(2).show();
}

function hideBoth() {
  $( ".form-group" ).eq(1).hide();
  $( ".form-group" ).eq(2).hide();
}
