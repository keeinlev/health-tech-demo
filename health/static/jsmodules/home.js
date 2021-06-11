window.onload = function() {
    $('#device-img').css({"opacity": "1"});
    $('.typography').css({"opacity": "1"});
    $('.action-button')[0].style.opacity = 1;
}
window.onscroll = function() {
    console.log(window.pageYOffset)
    if (window.pageYOffset > 0) {
        $('#main-nav').addClass('shadow');
    } else {
        console.log('here')
        $('#main-nav').removeClass('shadow');
    }
    if (window.pageYOffset > 120) {
        $('.typography2').css({"opacity": "1"});
    }
    if (window.pageYOffset > 350) {
        $('.instruction-box').css({"opacity": "1"});
    }
    if (window.pageYOffset > 500) {
        $('.action-button')[1].style.opacity = 1;
        try {
            $('.action-button')[2].style.opacity = 1; 
        } catch (error) {}
    }
}