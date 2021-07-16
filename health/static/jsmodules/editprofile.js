$('#id_sms_notis, #id_email_notis').on('change', function() {
    if ($('#id_sms_notis')[0].parentElement.classList.contains('off') && $('#id_email_notis')[0].parentElement.classList.contains('off')) {
        console.log('here');
        if (this.id == 'id_sms_notis') {
            document.getElementsByClassName('toggle')[0].click();
        } else if (this.id == 'id_email_notis') {
            document.getElementsByClassName('toggle')[1].click();
        }
        
    }
})
