window.onscroll = function() {
    console.log(window.pageYOffset)
    if (window.pageYOffset > 0) {
        $('#main-nav').addClass('shadow');
    } else {
        console.log('here')
        $('#main-nav').removeClass('shadow');
    }
}