$('.pharmacy-label').change(function() {
    if ($('#pharmacy-submit').prop('disabled')) {
        $('#pharmacy-submit').prop('disabled', false);
    }
    //console.log($(this).children(".pharmacy-radio").val());
    //console.log($('#pharmacy-map').attr('src'));
    old_url = $('#pharmacy-map').attr('src');
    new_place_id = $(this).children(".pharmacy-radio").val();
    ind = $('#pharmacy-map').attr('src').indexOf('&q=');
    new_url = old_url.slice(0, ind + 3); // remove old query text
    new_url = new_url.replace('search', 'place'); // change map mode
    new_url = new_url + 'place_id:' + new_place_id; // insert new query

    //console.log(ind);
    //console.log($('#pharmacy-map').attr('src').slice(0,ind + 3).replace('search', 'place') + 'place_id:' + $(this).children(".pharmacy-radio").val());
    $('#pharmacy-map').attr('src', new_url)
})
