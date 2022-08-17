/* .html document ready */
function mobileView() {
    var width_size = window.outerWidth;    
    if(width_size < 768) {
        $("#main_impression_img_layout").removeClass("col-8");
        $("#main_impression_list_layout").removeClass("col-4");
        $("#detail_content").removeClass("card");

        $("#main_impression_img_layout").addClass("col");
        $("#main_impression_list_layout").addClass("col mt-1");
    } else {
        $("#main_impression_img_layout").removeClass("col");
        $("#main_impression_list_layout").removeClass("col mt-1");

        $("#main_impression_img_layout").addClass("col-8");
        $("#main_impression_list_layout").addClass("col-4");
        $("#detail_content").addClass("card");
    }
    
    $(window).resize(function() {
        width_size = window.outerWidth;
        if(width_size < 768) {
            $("#main_impression_img_layout").removeClass("col-8");
            $("#main_impression_list_layout").removeClass("col-4");
            $("#detail_content").removeClass("card");
            
            $("#main_impression_img_layout").addClass("col");
            $("#main_impression_list_layout").addClass("col mt-1");
        } else {
            $("#main_impression_img_layout").removeClass("col");
            $("#main_impression_list_layout").removeClass("col mt-1");
            
            $("#main_impression_img_layout").addClass("col-8");
            $("#main_impression_list_layout").addClass("col-4");
            $("#detail_content").addClass("card");
        }
    });
}

function changeMainImpression(idx) {
    var news_id = $($(".rec_news_list_id")[idx]).text();
    var news_category = $($(".rec_news_list_category")[idx]).text();
    var news_title = $($(".rec_news_list_title")[idx]).text();
    var news_img_path = $($(".rec_news_list_img_path")[idx]).text()
    
    // console.log(news_title);
    // console.log(news_id);
    // console.log(capitalize(news_category));
    // console.log(news_img_path);
    
    $("#main_impression_id").text(news_id);
    $("#main_impression_category").text(capitalize(news_category));
    $("#main_impression_title").text(news_title);
    // $("#main_impression_img").css("background-image", 'url("' + news_img_path + '")');
    document.getElementById('main_impression_img').style.backgroundImage = `url("${news_img_path}")`;
}

$(document).ready(function () {
    mobileView();
    
    $("#main_impression_img").click(function() {
        var url = "/detail/" + $("#main_impression_id").text();
        $(location).attr("href", url);
    });
    
    $("#day_11").click(function() {
        $.post("/date", {date: "2019-11-11"}, function(data, status) {
            alert("success");
            window.location.reload();
        });
    });
    $("#day_12").click(function() {
        $.post("/date", {date: "2019-11-12"}, function(data, status) {
            alert("success");
            window.location.reload();
        });
    });
    $("#day_13").click(function() {
        $.post("/date", {date: "2019-11-13"}, function(data, status) {
            alert("success");
            window.location.reload();
        });
    });
    $("#day_14").click(function() {
        $.post("/date", {date: "2019-11-14"}, function(data, status) {
            alert("success");
            window.location.reload();
        });
    });
    $("#day_15").click(function() {
        $.post("/date", {date: "2019-11-15"}, function(data, status) {
            alert("success");
            window.location.reload();
        });
    });
});