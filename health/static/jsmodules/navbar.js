window.onscroll = function() {
    console.log(window.pageYOffset)
    if (window.pageYOffset > 0) {
        try {
            $('.notification').addClass('shadow');
            $('.notification').attr()
        } catch (error) {
            $('#main-nav').addClass('shadow');
        } 
    } else {
        try {
            $('.notification').removeClass('shadow');
            $('.notification').attr()
        } catch (error) {
            $('#main-nav').removeClass('shadow');
        }   
    }
}