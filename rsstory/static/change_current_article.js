function saveChanges(feed_id) {
    var page_id = $('input[name="start_page"]:checked').val();
    var url =  window.location.protocol + "//" + window.location.host + window.location.pathname;

    $.ajax({
        type    : 'POST',
        url     : url + "/update-place-in-feed",
        data: window.JSON.stringify({
            feed_id: feed_id,
            page_id: page_id,
        }),
        contentType: 'application/json; charset=utf-8',
        success : function(data){
            data = window.JSON.parse(data);
            $('#response').append("Changes Saved (may take a little while to take effect)");
        },
        dataType: "text"
    });
}
