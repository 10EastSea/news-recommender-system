/* algorithm function */
function isEmpty(str){  
    if(typeof str == "undefined" || str == null || str == "") return true;
    else return false ;
}

function saveImg(uri, filename) {
    var link = document.createElement('a');
    if(typeof link.download === 'string') {
        link.href = uri;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } else {
        window.open(uri);
    }
}