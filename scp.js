$(document).ready(function() {
  $("#cpa-form").submit(function(e){
    return false;
  });
  $('#submit').click(function () {
    $('#archive').submit();
    $('#time').submit();
    $('#archive').clear();
    $('#time').clear();
  });
});
