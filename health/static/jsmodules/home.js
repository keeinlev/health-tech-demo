window.onload = function() {
    $('#device-img').css({"opacity": "1"});
    $('.typography').css({"opacity": "1"});
    $('.action-button').css({"opacity": "1"});
}
window.onscroll = function() {
    if (window.pageYOffset > 120) {
        $('.typography2').css({"opacity": "1"});
    }
    if (window.pageYOffset > 150) {
        $('.instruction-box').css({"opacity": "1"});
    }
}