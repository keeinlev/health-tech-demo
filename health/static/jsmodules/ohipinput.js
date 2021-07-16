var lastkey;

$('#ohip').on('focus', function() {
    this.placeholder = '####-###-###-XX'
})
$('#ohip').on('blur', function() {
    this.placeholder = 'OHIP Number'
})
$('#ohip').on('keydown', function(e) {
    lastkey = e.key;
})
$('#ohip').on('input', function() {
    current = this.value
    console.log(current)
    if (current.length == 4 || current.length == 8 || current.length == 12) {
        if (lastkey == 'Backspace') {
            console.log('here')
            this.value = current.slice(0, current.length - 1);
        } else {
            this.value += '-';
        }
    }
    updated = this.value
    
    
    if (updated.length > 5 && updated.charAt(4) != '-') {
        this.value = updated.slice(0, 4) + '-' + updated.slice(5);
        updated = this.value
    }
    if (updated.length > 9 && updated.charAt(8) != '-') {
        this.value = updated.slice(0, 8) + '-' + updated.slice(9);
        updated = this.value
    }

    if (updated.length > 13 && updated.charAt(12) != '-') {
        this.value = updated.slice(0, 12) + '-' + updated.slice(13);
        updated = this.value;
    }
    
    
})