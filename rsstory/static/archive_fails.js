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

    // set captcha value
    var elem = document.getElementById("captcha");
    elem.value = grecaptcha.getResponse();
    grecaptcha.reset();

    $.ajax({
      type: "POST",
      url: window.location.href + '/report' ,
      data: window.JSON.stringify({
        url: $('#archive').val(),
        comments: $('#comments').val(),
        captcha: $('#captcha').val()
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
          $('#main_body').append('<span id="rss_output">URL reported successfully</span>');
        } else {
          $('#main_body').append('<span id="rss_output">Cross my heart, smack me dead, stick a lobster on my head, you managed to break the error reporting system! Please file a bug at <a href="https://github.com/Daphron/rsstory">https://github.com/Daphron/rsstory</a></span>');
        }
      },
      dataType: "text"
    });
  });
});
