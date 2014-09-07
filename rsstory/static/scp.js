$(document).ready(function() {
  $("#cpa-form").submit(function(e){
    return false;
  });
  $('#submit').click(function () {
    if ($('#rss_status').length) {
      $('#rss_status').remove();
    }
    $.ajax({
      type: "POST",
      url: window.location.href + "feed",
      data: window.JSON.stringify({
        url: $('#archive').val(),
        time: $('#time').val()
      }),
      contentType: 'application/json; charset=utf-8',
      success: function (data, status) {
        data = window.JSON.parse(data);
        if (status === "success" && (! (data.rss === 'Error'))) {
          console.log(window.location.href.slice(-1) + data.rss);
          $('#main_body').append("<a href=" + window.location.href.slice(0,-1) + data.rss + " id='rss_status'> Follow this link to your feed.</a>");
        } else {
          $('#main_body').append('<a id="rss_status"> Error</a>');
        }
      },
      dataType: "text"
    });
  });
});
