$(document).ready(function() {
  $("#cpa-form").submit(function(e){
    return false;
  });
  $('#submit').click(function () {
    if ($('#rss_status').length) {
      $('#rss_status').remove();
    }
    if ($('#rss_output').length) {
      $('#rss_output').remove();
    }
    $('#main_body').append('<a id="rss_status">Loading...</a>');
    $.ajax({
      type: "POST",
      url: window.location.href + "feed",
      data: window.JSON.stringify({
        title: $('#title').val(),
        url: $('#archive').val(),
        time: $('#time').val()
      }),
      contentType: 'application/json; charset=utf-8',
      success: function (data, status) {
        if ($('#rss_status').length) {
          $('#rss_status').remove();
        }
        if ($('#rss_output').length) {
          $('#rss_output').remove();
        }
        data = window.JSON.parse(data);
        if (status === "success" && (! (data.rss === 'Error'))) {
          $('#main_body').append("<span id='rss_output'><a href=" + window.location.href.slice(0,-1) + data.rss + "> <u>Follow this link to your feed</u></a> or <a rss_output' href=" + window.location.href.slice(0,-1) + data.preview + " target='_blank'> <u>check your new feed for correctness.</u></a></span>");
        } else {
          $('#main_body').append('<span id="rss_output"> Error</span>');
        }
      },
      dataType: "text"
    });
  });
});
