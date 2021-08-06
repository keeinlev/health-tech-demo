$(document.body).on("change", ".doctor-label", function() {
    let form = $("#bookform");
    $('#id_time').html('');
    
    $.ajax({
        url: form.attr("update-calendar-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
            let datesList = data['apptdates'];
            let consultations = data['consultations'];
            for (let i = 0; i < datesList.length; ++i) {
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
                //@ts-ignore
                $('#bookcalendar').calendar('refresh');
                //@ts-ignore
                $('#bookcalendar').calendar('set minDate', datesList[0]);
                //@ts-ignore
                $('#bookcalendar').calendar('refresh');
                //@ts-ignore
                $('#bookcalendar').calendar('set maxDate', datesList[datesList.length - 1]);
            }
            
            let str = '';
            for (let i = 0; i < consultations.length; i++) {
                str += `<option value='${consultations[i]}'>${consultations[i]}</option>\n`
            }
            $('#id_consultation').html(str);
            $('#booksubmit').addClass('display-hidden')
            console.log(data['d_id'])
            $('#id_doctor').val(data['d_id'])
        }
    });
})

function getApptTimes(date: Date | string) {
    //@ts-ignore
    let rawdate = $('#bookcalendar').calendar('get date');
    try {
        let day: number = rawdate.getDate();
        let month: number = rawdate.getMonth() + 1;
        let year: number = rawdate.getFullYear();
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
                    $('#booksubmit').addClass('display-hidden')
                } else {
                    $('#noappt').html('');
                    let keys = data['keys'];
                    let values = data['values'];
                    console.log(keys)
                    console.log(values)
                    let str = ''
                    for (let i = 0; i < keys.length; i++) {
                        str += `<option value='${keys[i]}'>${values[i]}</option>\n`
                    }
                    $('#id_time').html(str);
                    $('#booksubmit').removeClass('display-hidden')
                }
            }
        });
    } catch(err) {
        console.log(err);
    }
}

var today = new Date();
$('#bookcalendar')
    //@ts-ignore
    .calendar({
        type:'date',
        inline: true,
        onChange: function() {
            //@ts-ignore
            $('#bookcalendar').calendar('refresh');
            //@ts-ignore
            console.log($('#bookcalendar').calendar('get date'));
            //@ts-ignore
            getApptTimes($('#bookcalendar').calendar('get date'));
        }
    });

$("label").on('input', function() {
    let userHasPhone = true;
    if (this.getAttribute('for') == 'id_appt_type_0') {
        if (parseInt($('#bookform').attr('user-phone')) == 0) {
            userHasPhone = false;
        }
    }
    if (userHasPhone) {
        $('#first-next-button').prop('disabled', '');
        $('.phone-error').addClass('display-hidden');
    } else {
        $('#first-next-button').prop('disabled', 'disabled');
        $('.phone-error').removeClass('display-hidden');
    }
})

$('#doctor-filter-textbox').on('input', function(e) {
    $('#loadModal').css('display', 'block');
    let parent = <Node>$('.doctor-content')[0];
    $.ajax({
        dataType: 'json',
        data: {
            'search':(<HTMLInputElement>this).value,
            'selected': $('#id_doctor').val(),
        },
        url: this.getAttribute('doctor-filter-url'),
        success: function(data) {
            //let s = '';
            $('.doctor-content').html('');
            let selectedStillShown = false;
            for (let i=0; i < data['doctordata'].length; i++) {

                let doctor = data['doctordata'][i];
                let doctorFullName = (doctor['preferred_name'] ? doctor['preferred_name'] : doctor['first_name']) + ' ' + doctor['last_name'];

                let doctorLabel = document.createElement('label');
                doctorLabel.setAttribute("class", "doctor-label");

                let doctorRadio = document.createElement('input');
                doctorRadio.setAttribute("type", "radio");
                doctorRadio.setAttribute("value", doctor['pk']);
                doctorRadio.setAttribute("name", "doctor-id");
                doctorRadio.setAttribute("class", "doctor-radio");

                let doctorContainer = document.createElement("div");
                doctorContainer.setAttribute("class", "doctor-container");

                let doctorName = document.createElement("h4");
                doctorName.innerText = doctorFullName;

                let doctorDescription = document.createElement("p");
                doctorDescription.innerHTML = `<b>Qualifications:</b><br>\n${doctor['qualifications']}<br>\n<b>Consultations:</b><br>\n${doctor['consultations']}<br>\n<b>Languages:</b><br>\n${doctor['languages']}`

                doctorContainer.appendChild(doctorName);
                doctorContainer.appendChild(document.createElement('br'));
                doctorContainer.appendChild(doctorDescription);
                doctorContainer.appendChild(document.createElement('br'));

                doctorLabel.appendChild(doctorRadio);
                doctorLabel.appendChild(doctorContainer);

                parent.appendChild(doctorLabel);

                if (doctor['pk'] == data['selected']) {
                    doctorLabel.click();
                    selectedStillShown = true;
                }

                //s += `<label class=\"doctor-label\">\n<input type=\"radio\" value=\"${doctor['pk']}\" name=\"doctor-id\" class=\"doctor-radio\">\n<div class=\"doctor-container\">\n<h4>${doctorFullName}</h4><br>\n<p><b>Qualifications:</b><br>\n${doctor['qualifications']}<br>\n<b>Consultations:</b><br>\n${doctor['consultations']}<br>\n<b>Languages:</b><br>\n${doctor['languages']}</p><br>\n</div>\n</label>\n`
            }
            if (!selectedStillShown) {
                $('#id_doctor').val(null);
                $('#calendar-cont').addClass('hidden');
                $('#booksubmit').addClass('display-hidden');
            }
            //console.log(s);
            //$('.doctor-content').html(s);
            $('#loadModal').css('display', 'none');
        }
    })
})