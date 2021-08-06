$('.doctor-label').on("change", function () {
    var form = $(this).closest("form");
    $('#id_time').html('');
    $.ajax({
        url: form.attr("update-calendar-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
            var datesList = data['apptdates'];
            var consultations = data['consultations'];
            for (var i = 0; i < datesList.length; ++i) {
                datesList[i] = datesList[i].split('-');
                datesList[i] = new Date(datesList[i][0], parseInt(datesList[i][1]) - 1, datesList[i][2]);
            }
            console.log(datesList);
            if (datesList.length == 0) {
                $('#calendar-cont').addClass('hidden');
                $('#apptsempty').html('This doctor is unavailable');
            }
            else {
                $('#apptsempty').html('');
                $('#calendar-cont').removeClass('hidden');
                $('#bookcalendar').calendar('refresh');
                $('#bookcalendar').calendar('set minDate', datesList[0]);
                $('#bookcalendar').calendar('refresh');
                $('#bookcalendar').calendar('set maxDate', datesList[datesList.length - 1]);
                //$('#bookcalendar').calendar('set minDate', datesList[0]);
                //$('#bookcalendar').calendar('refresh');
                //$('#bookcalendar').calendar('set date', datesList[0]);
                //$('#bookcalendar').calendar('refresh');
            }
            var str = '';
            for (var i = 0; i < consultations.length; i++) {
                str += "<option value='" + consultations[i] + "'>" + consultations[i] + "</option>\n";
            }
            $('#id_consultation').html(str);
            $('#booksubmit').addClass('display-hidden');
            console.log(data['d_id']);
            $('#id_doctor').val(data['d_id']);
        }
    });
});
function getApptTimes(date) {
    var rawdate = $('#bookcalendar').calendar('get date');
    try {
        var day = rawdate.getDate();
        var month = rawdate.getMonth() + 1;
        var year = rawdate.getFullYear();
        date = year + '-' + String(month).padStart(2, '0') + '-' + String(day).padStart(2, '0');
        console.log(date);
        $('input[name="date"]').val(date);
        $.ajax({
            url: $('#bookform').attr("find-times-url"),
            data: $('#bookform').serialize(),
            dataType: 'json',
            success: function (data) {
                if (data['message']) {
                    $('#id_time').html('');
                    $('#noappt').html(data['message']);
                    $('#booksubmit').addClass('display-hidden');
                }
                else {
                    $('#noappt').html('');
                    var keys = data['keys'];
                    var values = data['values'];
                    console.log(keys);
                    console.log(values);
                    var str = '';
                    for (var i = 0; i < keys.length; i++) {
                        str += "<option value='" + keys[i] + "'>" + values[i] + "</option>\n";
                    }
                    $('#id_time').html(str);
                    $('#booksubmit').removeClass('display-hidden');
                }
            }
        });
    }
    catch (err) {
        console.log(err);
    }
}
var today = new Date();
$('#bookcalendar')
    .calendar({
    type: 'date',
    inline: true,
    onChange: function () {
        $('#bookcalendar').calendar('refresh');
        console.log($('#bookcalendar').calendar('get date'));
        getApptTimes($('#bookcalendar').calendar('get date'));
    }
});
$("label").on('input', function () {
    var userHasPhone = true;
    if (this.getAttribute('for') == 'id_appt_type_0') {
        if (parseInt($('#bookform').attr('user-phone')) == 0) {
            userHasPhone = false;
        }
    }
    if (userHasPhone) {
        $('#first-next-button').prop('disabled', '');
        $('.phone-error').addClass('display-hidden');
    }
    else {
        $('#first-next-button').prop('disabled', 'disabled');
        $('.phone-error').removeClass('display-hidden');
    }
});
$('#doctor-filter-textbox').on('input', function (e) {
    $.ajax({
        dataType: 'json',
        data: {
            'search': this.value
        },
        url: this.getAttribute('doctor-filter-url'),
        success: function (data) {
            var s = '';
            for (var i = 0; i < data['doctordata'].length; i++) {
                var doctor = data['doctordata'][i];
                var doctorFullName = (doctor['preferred_name'] ? doctor['preferred_name'] : doctor['first_name']) + ' ' + doctor['last_name'];
                s += "<label class=\"doctor-label\">\n<input type=\"radio\" value=\"" + doctor['pk'] + "\" name=\"doctor-id\" class=\"doctor-radio\">\n<div class=\"doctor-container\">\n<h4>" + doctorFullName + "</h4><br>\n<p><b>Qualifications:</b><br>\n" + doctor['qualifications'] + "<br>\n<b>Consultations:</b><br>\n" + doctor['consultations'] + "<br>\n<b>Languages:</b><br>\n" + doctor['languages'] + "</p><br>\n</div>\n</label>\n";
            }
            console.log(s);
            $('.doctor-content').html(s);
        }
    });
});
