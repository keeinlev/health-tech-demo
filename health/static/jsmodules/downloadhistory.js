$('#id_entire_day').on("change", function() {
    if ($('.toggle').hasClass('btn-success')) {
        $('#id_starttime').prop('disabled', 'disabled')
        $('#id_endtime').prop('disabled', 'disabled')
    } else {
        $('#id_starttime').prop('disabled', '')
        $('#id_endtime').prop('disabled', '')
    }
})