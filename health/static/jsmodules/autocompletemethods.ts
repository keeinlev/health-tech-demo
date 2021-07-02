$(document).on('click', '.autocomplete-item', function() {
    let hiddenInput = $('#id_consultations');
    if (this.className.includes('language-item')) {
        hiddenInput = $('#id_languages');
    }
    let str = this.innerText.slice(3);
    let current = hiddenInput.val().toString();
    let start = current.indexOf(str);
    let end = start + str.length + 2;
    if (end > current.length && start > 0) {
        start = start - 2;
    }
    hiddenInput.val(current.slice(0, start) + current.slice(end));
    this.remove();
});
export default function autocomplete(inp:HTMLInputElement, arr:string[]) {
    let currentFocus: number;
    inp.addEventListener("input", function(e) {
        let a, b: HTMLElement;
        let val = this.value;
        closeAllLists();
        if (!val) { return false;}
        currentFocus = -1;
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        this.parentNode.appendChild(a);
        for (let i = 0; i < arr.length; i++) {
            if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                b = document.createElement("DIV");
                b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
                b.innerHTML += arr[i].substr(val.length);
                b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
                b.addEventListener("click", function(e) {
                    inp.value = this.getElementsByTagName("input")[0].value;
                    closeAllLists();
                });
                a.appendChild(b);
            }
        }
    });
    inp.addEventListener("keydown", function(e: KeyboardEvent) {
        let x: HTMLElement = document.getElementById(this.id + "autocomplete-list");
        if (x) {
            let y = x.getElementsByTagName("div");
            
            if (e.key == "ArrowDown") {
                currentFocus++;
                addActive(y);
            } else if (e.key == "ArrowUp") {
                currentFocus--;
                addActive(y);
            } else if (e.key == "Enter") {
                e.preventDefault();
                if (currentFocus > -1) {
                    if (y) y[currentFocus].click();
                }
                if (this.id == 'consult-input') {
                    addToHidden(this, <HTMLInputElement>document.getElementById('id_consultations'), 'current-consults');
                } else if (this.id == 'language-input') {
                    addToHidden(this, <HTMLInputElement>document.getElementById('id_languages'), 'current-languages');
                }
            }
        }
    });
    function addActive(x: HTMLCollection) {
        if (!x) return false;
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        x[currentFocus].classList.add("autocomplete-active");
    }
    function removeActive(x: HTMLCollection) {
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }
    function closeAllLists(elmnt?: EventTarget) {
        let x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }
    document.addEventListener("click", function (e: MouseEvent) {
        closeAllLists(e.target);
    });
}
function addToHidden(addInput: HTMLInputElement, to: HTMLInputElement, label: string) {
    //addInput = document.getElementById('consult-input');
    //to = document.getElementById('id_consultations');
    if (!to.value.includes(addInput.value)) {
        if (to.value == '') {
            to.value = addInput.value;
        } else {
            to.value += ', ' + addInput.value;
        }
        document.getElementById(label).innerHTML += "\n<div class='autocomplete-item" + ((label == 'current-languages') ? " language-item" : " consult-item") + "'>" + "&times;&nbsp;&nbsp;" + addInput.value + "</div>";
    }
    addInput.value = '';
    
}