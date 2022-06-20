/* algorithm function */
function isEmpty(str){  
    if(typeof str == "undefined" || str == null || str == "") return true;
    else return false ;
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}