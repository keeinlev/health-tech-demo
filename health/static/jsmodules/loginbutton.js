button = document.getElementById('login-submit');

document.onkeyup = function(e) {
    if ($('#id_username').val() && $('#id_password').val()) {
        button.disabled = false;
    } else {
        button.disabled = true;
    }
}