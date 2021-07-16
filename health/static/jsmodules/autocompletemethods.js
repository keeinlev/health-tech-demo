$(document).on('click', '.autocomplete-item', function () {
    var hiddenInput = $('#id_consultations');
    if (this.className.includes('language-item')) {
        hiddenInput = $('#id_languages');
    }
    var str = this.innerText.slice(3);
    var current = hiddenInput.val().toString();
    var start = current.indexOf(str);
    var end = start + str.length + 2;
    if (end > current.length && start > 0) {
        start = start - 2;
    }
    hiddenInput.val(current.slice(0, start) + current.slice(end));
    this.remove();
});
function autocomplete(inp, arr) {
    var currentFocus;
    inp.addEventListener("input", function (e) {
        var a, b;
        var val = this.value;
        closeAllLists();
        if (!val) {
            return false;
        }
        currentFocus = -1;
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        this.parentNode.appendChild(a);
        for (var i = 0; i < arr.length; i++) {
            if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                b = document.createElement("DIV");
                
                b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
                b.innerHTML += arr[i].substr(val.length);
                if (inp.id == 'consult-input') {
                    b.setAttribute('class', 'autocomplete-dropdown-item consult-dropdown-item')
                    b.innerHTML += "<input type='hidden' class='consult' value='" + arr[i] + "'>";
                }
                else if (inp.id == 'language-input') {
                    b.setAttribute('class', 'autocomplete-dropdown-item language-dropdown-item')
                    b.innerHTML += "<input type='hidden' class='language' value='" + arr[i] + "'>";
                }
                b.addEventListener("click", function (e) {
                    inp.value = this.getElementsByTagName("input")[0].value;
                    addToHiddenWrapper(inp);
                    inp.value = '';
                    closeAllLists();
                });
                a.appendChild(b);
            }
        }
    });
    inp.addEventListener("keydown", function (e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) {
            var y = x.getElementsByTagName("div");
            if (e.key == "ArrowDown") {
                currentFocus++;
                addActive(y);
            }
            else if (e.key == "ArrowUp") {
                currentFocus--;
                addActive(y);
            }
            else if (e.key == "Enter") {
                e.preventDefault();
                if (currentFocus > -1) {
                    if (y){
                        y[currentFocus].click();
                    }
                } else {
                    // if input is not in the autocomplete list
                    addToHiddenWrapper(inp);
                }
            }
        }
    });
    function addActive(x) {
        if (!x)
            return false;
        removeActive(x);
        if (currentFocus >= x.length)
            currentFocus = 0;
        if (currentFocus < 0)
            currentFocus = (x.length - 1);
        x[currentFocus].classList.add("autocomplete-active");
    }
    function removeActive(x) {
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }
    function closeAllLists(elmnt) {
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });
}
function addToHidden(addInput, to, label) {
    //addInput = document.getElementById('consult-input');
    //to = document.getElementById('id_consultations');
    display = document.getElementById(label);
    if (!to.value.includes(addInput.value)) {
        if (to.value == '') {
            to.value = addInput.value;
        }
        else {
            to.value += ', ' + addInput.value;
        }
        if (display.innerHTML.includes('None')){
            display.innerHTML = '';
        }
        display.innerHTML += "\n<div class='autocomplete-item" + ((label == 'current-languages') ? " language-item" : " consult-item") + "'>" + "&times;&nbsp;&nbsp;" + addInput.value + "</div>";
    }
    addInput.value = '';
}
function addToHiddenWrapper(x) {
    if (x.id == 'consult-input') {
        addToHidden(x, document.getElementById('id_consultations'), 'current-consults');
    }
    else if (x.id == 'language-input') {
        addToHidden(x, document.getElementById('id_languages'), 'current-languages');
    }
}