/* detail.html document ready */
function mobileView() {
    var width_size = window.outerWidth;    
    if(width_size < 768) {
        $("#main_impression_img_layout").removeClass("col-8");
        $("#main_impression_list_layout").removeClass("col-4");

        $("#main_impression_img_layout").addClass("col");
        $("#main_impression_list_layout").addClass("col mt-1");
    } else {
        $("#main_impression_img_layout").removeClass("col");
        $("#main_impression_list_layout").removeClass("col mt-1");

        $("#main_impression_img_layout").addClass("col-8");
        $("#main_impression_list_layout").addClass("col-4");
    }
    
    $(window).resize(function() {
        width_size = window.outerWidth;
        if(width_size < 768) {
            $("#main_impression_img_layout").removeClass("col-8");
            $("#main_impression_list_layout").removeClass("col-4");
            
            $("#main_impression_img_layout").addClass("col");
            $("#main_impression_list_layout").addClass("col mt-1");
        } else {
            $("#main_impression_img_layout").removeClass("col");
            $("#main_impression_list_layout").removeClass("col mt-1");
            
            $("#main_impression_img_layout").addClass("col-8");
            $("#main_impression_list_layout").addClass("col-4");
        }
    });
}

$(document).ready(function () {
    mobileView();
});