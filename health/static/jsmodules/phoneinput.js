var lastkey;

$('#phone').on('focus', function() {
    this.placeholder = '(###) ###-####'
})
$('#phone').on('blur', function() {
    this.placeholder = 'Phone Number'
})
$('#phone').on('keydown', function(e) {
    lastkey = e.key;
})
$('#phone').on('input', function() {
    current = this.value
    if (current.length == 5 && lastkey == 'Backspace') {
        this.value = current.slice(1).slice(0, current.length - 3);
    }
    if (current.length == 3) {
        this.value = '(' + current + ') ';
    }
    if (current.length == 9) {
        if (lastkey == 'Backspace') {
            console.log('here')
            this.value = current.slice(0, current.length - 1);
        } else {
            this.value += '-';
        }
    }
    updated = this.value
    var numbers = collectInts(updated)

    if (numbers.length > 3 && (updated.charAt(0) != '(' || updated.charAt(4) != ')')) {
        console.log(updated)
        updated = collectInts(updated);
        console.log(updated)
        this.value = '(' + updated.slice(0, 3) + ') ' + updated.slice(3);
        updated = this.value
    }

    if (updated.length > 10 && updated.charAt(9) != '-') {
        updated = updated.slice(0,6) + collectInts(updated.slice(6))
        this.value = updated.slice(0, 9) + '-' + updated.slice(9);
        updated = this.value
    }

    
    
})

function collectInts(str) {
    var newstr = '';
    for (var i = 0; i < str.length; i++) {
        
        if (!isNaN(parseInt(str.charAt(i)))) {
            console.log(parseInt(str.charAt(i)))
            newstr += str.charAt(i);
        }
    }
    return newstr;
}