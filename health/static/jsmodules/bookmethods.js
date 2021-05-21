$('.doctor-label').change(function() {
    var form = $(this).closest("form");
    $('#id_time').html('');
    
    $.ajax({
        url: form.attr("update-calendar-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
            datesList = data['apptdates'];
            consultations = data['consultations'];
            for (i = 0; i < datesList.length; ++i) {
                datesList[i] = datesList[i].split('-');
                datesList[i] = new Date(datesList[i][0], parseInt(datesList[i][1]) - 1, datesList[i][2]);
            }
            console.log(datesList);
            if (datesList.length == 0) {
                $('#calendar-cont').addClass('hidden');
                $('#apptsempty').html('This doctor is unavailable')
            } else {
                $('#apptsempty').html('')
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
            
            str = '';
            for (i = 0; i < consultations.length; i++) {
                str += `<option value='${consultations[i]}'>${consultations[i]}</option>\n`
            }
            $('#id_consultation').html(str);
            $('#booksubmit').addClass('hidden')
            console.log(data['d_id'])
            $('#id_doctor').val(data['d_id'])
        }
    });
})

function getApptTimes(date) {
    rawdate = $('#bookcalendar').calendar('get date');
    try {
        day = rawdate.getDate();
        month = rawdate.getMonth() + 1;
        year = rawdate.getFullYear();
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
                    $('#booksubmit').addClass('hidden')
                } else {
                    $('#noappt').html('');
                    keys = data['keys'];
                    values = data['values'];
                    console.log(keys)
                    console.log(values)
                    str = ''
                    for (i = 0; i < keys.length; i++) {
                        str += `<option value='${keys[i]}'>${values[i]}</option>\n`
                    }
                    $('#id_time').html(str);
                    $('#booksubmit').removeClass('hidden')
                }
            }
        });
    } catch(err) {
        console.log(err);
    }
}

var today = new Date();
$('#bookcalendar')
    .calendar({
        type:'date',
        inline: true,
        onChange: function() {
            $('#bookcalendar').calendar('refresh');
            console.log($('#bookcalendar').calendar('get date'));
            getApptTimes($('#bookcalendar').calendar('get date'));
        }
    });