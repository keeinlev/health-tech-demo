function filterNumbers(s) {
    var newstr = '';
    for (var i = 0; i < s.length; i++) {
        if (s[i] >= '0' && s[i] <= '9') {
            newstr += s[i];
        }
    }
    return newstr;
}

$('#id_sms_notis, #id_email_notis').on('change', function() {
    var emailToggle = document.getElementsByClassName('toggle')[0];
    var smsToggle = document.getElementsByClassName('toggle')[1];
    var smsIsOn = !$('#id_sms_notis')[0].parentElement.classList.contains('off');
    var emailIsOn = !$('#id_email_notis')[0].parentElement.classList.contains('off');
    var phoneNumberValid = filterNumbers($('#phone').val()).length == 10;
    if (!smsIsOn && !emailIsOn) {
        if (this.id == 'id_sms_notis') {
            emailToggle.click();
        } else if (this.id == 'id_email_notis') {
            if (phoneNumberValid) {
                smsToggle.click();
            } else {
                $('#phone-valid-alert').addClass('red-text');
                $('#phone-valid-alert').addClass('shake');
                emailToggle.click();
            }
        }
    } else if (smsIsOn) {
        if (!phoneNumberValid) {
            $('#phone-valid-alert').addClass('red-text');
            $('#phone-valid-alert').addClass('shake');
            smsToggle.click();
        }
    }
})

$('#email').on('input', function() {
    if ($('#email').val() != $('#id_init_email').val()) {
        $('#change-email-alert').removeClass('display-hidden');
    } else {
        $('#change-email-alert').addClass('display-hidden');
    }
})

$('#phone').on('input', function() {
    var smsToggle = document.getElementsByClassName('toggle')[1];
    var smsIsOn = !$('#id_sms_notis')[0].parentElement.classList.contains('off');
    if (filterNumbers(this.value).length == 10) {
        $('#phone-valid-alert').removeClass('red-text');
        $('#phone-valid-alert').removeClass('shake');
    } else {
        $('#phone-valid-alert').addClass('red-text');
        $('#phone-valid-alert').addClass('shake');
        if (smsIsOn) {
            smsToggle.click();
        }
    }
})