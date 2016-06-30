function saveChanges(id) {
    var row = document.getElementById(id);
    var cells = row.getElementsByTagName("td");
    var title = cells[0].innerText;
    var time_between = cells[5].innerText;
    var url =  window.location.protocol + "//" + window.location.host + window.location.pathname;

    $.ajax({
        type    : 'POST',
        url     : url + "/update-feed",
        data: window.JSON.stringify({
            feed_id: id,
            title: title,
            time_between: time_between
        }),
        contentType: 'application/json; charset=utf-8',
        success : function(data){
            data = window.JSON.parse(data);
            $('#response').append("<p>Changes Saved</p>");
        },
        dataType: "text"
    });
}

function changeCurrentArticle(id) {
    var url =  window.location.protocol + "//" + window.location.host + window.location.pathname;
    window.location = url + "/change-current-article?id=" + id
}

function deleteFeed(id) {
    var url =  window.location.protocol + "//" + window.location.host + window.location.pathname;
    window.location = url + "/delete-feed?id=" + id
}
