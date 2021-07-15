var today = new Date();
var todayISO = today.toISOString().split('T')[0];

window.onload = function() {
    document.getElementById('id_startdate').setAttribute('min', todayISO);
    document.getElementById('id_c_startdate').setAttribute('min', todayISO);
}

$('#id_startdate').on("change", function() {
    var minEndDate = $('#id_startdate').val();
    document.getElementById('id_enddate').setAttribute('min', minEndDate);
});
$('#id_c_startdate').on("change", function() {
    var minEndDate = $('#id_c_startdate').val();
    document.getElementById('id_c_enddate').setAttribute('min', minEndDate);
});

$('.cancel-mult-fields').on("change", function() {
    filled = true;
    for (var elem=0; elem < $('.cancel-mult-fields').length; elem++) {
        if (!$('.cancel-mult-fields')[elem].value) {
            filled = false;
            break;
        }
    }
    if (filled) {
        form_url = $('#cancelmultform').attr("get-reason-url");
        form_data = $('#cancelmultform').serialize();
        cancel_needs_reason(form_url, form_data);
    }
})

function cancel_needs_reason(form_url, form_data) {
    $.ajax({
        url: form_url,
        data: form_data,
        dataType: 'json',
        success: function(data) {
            if (data['needs_reason']) {
                console.log('reason')
                $('#id_reason').val('');
                $('#reason-input').removeClass('display-hidden');
            } else {
                $('#id_reason').val('`');
                $('#reason-input').addClass('display-hidden');
            }
        }
    })
}

$('#bookcalendar').calendar({
    type: 'date',
    minDate: new Date(today.getFullYear(), today.getMonth(), today.getDate()),
    //maxDate: new Date(today.getFullYear(), today.getMonth(), today.getDate() + (getTotalDays(today.getMonth(), today.getYear()) - today.getDate())),
    inline: true,
    onChange: function() {
        $('#bookcalendar').calendar('refresh');
        if ($('#bookcalendar').calendar('get date')) {
            fetchAppts();
        }
        checkDate();
        $('#booksubmit').addClass("display-hidden");
        $('#already-booked').html('');
    }
});

function updateApptTable(details) {
    str = '';
    for (i = 0; i < details.length; ++i) {
        str += '<tr class="inforow">\n<td class="infocell">' + details[i]['date'] + '</td>';
        str += '\n    <td class="infocell">' + details[i]['time'] + '</td>';
        str += '\n    <td class="infocell">' + details[i]['booked'] + '</td>';
        str += '\n    <td class="infocell">' + details[i]['patient'] + '</td>';
        str += '\n    <td class="infocell"><a href="' + details[i]['detailsurl'] + '">Details</a></td>';
        str += '\n</tr>\n';
    }
    if (str) {
        $(str).appendTo( "#appointment-table" );
    } else {
        $('#default-row').removeClass('display-hidden');
    }
}

$('#search-bar').on("keyup", function() {
    bar = $('#search-bar').val();
    $('#patient-search').val(bar);
    if (bar != '') {
        rawdate = $('#bookcalendar').calendar('get date');
        date = 0;
        if (rawdate) {
            day = rawdate.getDate();
            month = rawdate.getMonth() + 1;
            year = rawdate.getFullYear();
            date = year + '-' + String(month).padStart(2, '0') + '-' + String(day).padStart(2, '0');
        }
        $('#default-row').addClass('display-hidden');
        $('.inforow').remove();
        $('input[name="date"]').val(date);
        $.ajax({
            url: $('#bookform').attr("get-patient-appts-url"),
            data: $('#bookform').serialize(),
            dataType: 'json',
            success: function (data) {
                updateApptTable(data['apptdata'])
            }
        });
    } else {
        $('.inforow').remove();
        fetchAppts();
    }
});

function fetchAppts() {
    rawdate = $('#bookcalendar').calendar('get date');
    day = rawdate.getDate();
    month = rawdate.getMonth() + 1;
    year = rawdate.getFullYear();
    date = year + '-' + String(month).padStart(2, '0') + '-' + String(day).padStart(2, '0');
    $('#default-row').addClass('display-hidden');
    $('.inforow').remove();
    $('input[name="date"]').val(date);
    $.ajax({
        url: $('#bookform').attr("get-dates-url"),
        data: $('#bookform').serialize(),
        dataType: 'json',
        success: function (data) {
            updateApptTable(data['apptdata'])
        }
    });
}

function clearCalendar() {
    $("#bookcalendar").calendar("clear");
    $('#booksubmit').addClass("display-hidden");
}

$('#id_time').change(function() {
    $('#already-booked').html('');
    checkDate();
})

function checkDate() {
    rawdate = $('#bookcalendar').calendar('get date');
    try {
        day = rawdate.getDate();
        month = rawdate.getMonth() + 1;
        year = rawdate.getFullYear();
        date = year + '-' + String(month).padStart(2, '0') + '-' + String(day).padStart(2, '0');
        $('input[name="date"]').val(date);

        $.ajax({
            url: $('#bookform').attr("check-date-url"),
            data: $('#bookform').serialize(),
            dataType: 'json',
            success: function (data) {
                $('#already-booked').html(data['message']);
                if (data['valid']) {
                    if (data['booked']) {
                        $('#already-booked').attr("style", "color: red");
                        $('#booksubmit').addClass("display-hidden");
                    } else {
                        $('#already-booked').attr("style", "color: green");
                        $('#booksubmit').removeClass("display-hidden");
                    }
                } else {
                    $('#already-booked').attr("style", "color: red");
                    $('#booksubmit').addClass("display-hidden");
                }
                
            }
        });
    }
    catch(err) {
        $('#already-booked').attr("style", "color: red");
        $('#already-booked').html("Please select a date from the calendar.");
    }
}

var prevGroup = 'all';
$('#upcoming-filter').on('change', function() {
	var group = this.value;
    var prevJQ = $(`.appointment-box[appt-group=${prevGroup}]`);
    if (prevJQ.length) {
        prevJQ.addClass('display-hidden');
    } else {
        $(`#${prevGroup}-empty`).addClass('display-hidden');
    }
    
    var newgroup = $(`.appointment-box[appt-group=${group}]`);
    if (newgroup.length) {
        newgroup.removeClass('display-hidden');
    } else {
        $(`#${group}-empty`).removeClass('display-hidden');
    }
    prevGroup = group;
})