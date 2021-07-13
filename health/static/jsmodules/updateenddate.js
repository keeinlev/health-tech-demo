$('#id_starttime, #id_c_starttime').on("change", function() {
    //if (this.value > $('#id_endtime').val()) {
    if (this.id == 'id_starttime') {
        form = $('#bookmultform');
        console.log(this.classList)
        if (this.classList.contains('dl_time')) {
            form = $('#dlform')
        }
    } else if (this.id == 'id_c_starttime') {
        form = $('#cancelmultform')
    }
    form_url = form.attr("update-end-date-url");
    form_data = form.serialize();
    update_end_date(form_url, form_data);
    //}
});
// $('#id_c_starttime').on("change", function() {
//     //if (this.value > $('#id_c_endtime').val()) {
//     form_url = $('#cancelmultform').attr("update-end-date-url");
//     form_data = $('#cancelmultform').serialize();
//     update_end_date(form_url, form_data);
//     //}
// });
function update_end_date(form_url, form_data) {
    $.ajax({
        url: form_url,
        data: form_data,
        dataType: 'json',
        success: function(data) {
            keys = data['keys'];
            values = data['values'];
            str = ''
            for (i = 0; i < keys.length; i++) {
                str += `<option value='${keys[i]}'`
                if (data['start_is_lesser'] && keys[i] == data['initial_end']) {
                    str += ' selected'
                }
                str += `>${values[i]}</option>\n`
            }
            if (data['is_cancel']) {
                $('#id_c_endtime').html('');
                $('#id_c_endtime').html(str);
            } else {
                $('#id_endtime').html('');
                $('#id_endtime').html(str);
            }
        }
    })
}
