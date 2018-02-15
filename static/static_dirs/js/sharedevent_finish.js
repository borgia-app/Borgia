$(updateForm()); // On laod

$("#id_type_payment").change(function(){
         updateForm();
    });

function updateForm() {
  var selected = $("#id_type_payment option:selected").val();
  switch (selected) {
    case "pay_by_total":
      $( ".form-group" ).eq(1).show();
      $( ".form-group" ).eq(2).hide();
      break;
    case "pay_by_ponderation":
      $( ".form-group" ).eq(1).hide();
      $( ".form-group" ).eq(2).show();
      break;
    case "no_payment":
      $( ".form-group" ).eq(1).hide();
      $( ".form-group" ).eq(2).hide();
      break;
    };
};
