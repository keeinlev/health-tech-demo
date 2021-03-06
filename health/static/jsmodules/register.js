var pass1 = document.getElementById('password1');
var pass2 = document.getElementById('password2');
var passmatchmsg = document.getElementById('password-match-help');

var email1 = document.getElementById('email1');
var email2 = document.getElementById('email2');
var emailmatchmsg = document.getElementById('email-match-help');

var subbtn = document.getElementById('register-submit');

var formelements = document.getElementsByClassName('formcontrol');

var match_pass = function() {
    if (pass1.value || pass2.value) {
        if ((pass1.value != pass2.value) || (pass1.value.length < 8) || (pass1.value.length > 16)) {
            pass1.style.borderColor = 'red';
            pass2.style.borderColor = 'red';
            $('#password-match-help').removeClass('display-hidden');
            return false;
        } else {
            pass1.style.borderColor = 'green';
            pass2.style.borderColor = 'green';
            $('#password-match-help').addClass('display-hidden');
            return true;
        }
    }
};

var match_email = function() {
    if (email1.value || email2.value) {
        if (email1.value != email2.value) {
            email1.style.borderColor = 'red';
            email2.style.borderColor = 'red';
            $('#email-match-help').removeClass('display-hidden');
            return false;
        }
        else {
            email1.style.borderColor = 'green';
            email2.style.borderColor = 'green';
            $('#email-match-help').addClass('display-hidden');
            return true;
        }
    }
};

var unique_fields = function (form) {
    $.ajax({
        url: form.attr("data-validate-email-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
            if (data.email_is_taken || data.ohip_is_taken) {
                $('.not-unique').html(data.error_message);
                $('.not-unique').removeClass('display-hidden');
                email1.style.borderColor = 'red';
                email2.style.borderColor = 'red';
            } else {
                $('.not-unique').html('');
                $('.not-unique').addClass('display-hidden');
            }
        }
    });
};
emailmatch = false;
passmatch = false;

$('.formcontrol, .next').on("input click", function(e) {
    
    var filled = true;

    if (!$(this).attr('class').includes('next') && ($(this).attr('class').includes('email-inputs') || $(this).attr('id').includes('ohip'))) {
        if ($(this).attr('class').includes('email-inputs')) {
            emailmatch = match_email();
            if (this.value.includes('@')) {
                unique_fields($(this).closest("form"));
            }
        } else if ($('#ohip').val().length == 15) {
            unique_fields($(this).closest("form"));
        }
        
    } else if ($(this).attr('class').includes('pass-inputs')) {
        passmatch = match_pass();
    } else {
        emailmatch=match_email();
        unique_fields($(this).closest('form'));
        passmatch=match_pass()
    }

    for (elem=0; elem < formelements.length; ++elem) {
        if (!formelements[elem].value && formelements[elem].hasAttribute('required')) {
            filled = false;
            break;
        }
    }
    if (filled && emailmatch && passmatch) {
        subbtn.disabled = false;
    } else {
        subbtn.disabled = true;
    }
    
});

$('#phone').on("focus", function() {
    $('#phone-help').removeClass('display-hidden');
})
