function leapYear(year){
    if (years / 400) {
        return true;
    }
    else if (years / 100) {
        return false;
    }
    else if (years / 4) {
        return true;
    }
    else {
        return false;
    }
}
var thirty_one = [1, 3, 5, 7, 8, 10, 12];
var thirty = [4, 6, 9, 11];
var getTotalDays = function(month, year) {
    if (month in thirty_one) {
        return 31;
    } else if (month in thirty) {
        return 30;
    } else if (leapYear(year)) {
        return 29;
    } else {
        return 28;
    }
}