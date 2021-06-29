window.onscroll = function() {
    console.log(window.pageYOffset)
    if (window.pageYOffset > 0) {
        $('#main-nav').addClass('shadow');
    } else {
        $('#main-nav').removeClass('shadow');
    }
}