var consults = ['Online Walk-In Appointment', 'Abrasions', 'Acid Reflux', 'Acne', 'Allergies', 'Asthma', 'Bacterial Vaginosis', 'Birth Control/Plan B', 'Body Aches', 'Bronchitis', 'Bug Bites', 'Cankers in Mouth', 'Cannabis Consult', 'Cataracts', 'Cholesterol Visit', 'Cold Sores', 'Concussion', 'COPD', 'Coronavirus', 'Coughing', 'Dehydration', 'Diarrhea', 'Earache', 'Emphysema', 'Erectile Dysfunction', 'Exercise Counseling', 'Eye Infection', 'Eye Issues', 'Fertility Optimization', 'Fever', 'Flu', 'Follow Up Appointment', 'Fracture', 'Frostbite', 'Glaucoma', 'Gout Flare Up', 'HPV Vaccination Consultation', 'Hair Loss', 'Head Lice', 'Headaches and Migraines', 'Hives', 'Hormone Health', 'Hypertension', 'Hypoactive Sexual Desire Disorder', 'Impetigo', 'Insomnia', 'Internal Medicine Consultation', 'Joint, Muscle Pain or Inflammation', 'Leg Pain', 'Macular Degeneration', 'Medical Device Prescriptions', 'Medical Forms', 'Menopause Consult', 'Mental Health Counselling', 'Nasal Congestion', 'Nausea', 'Nutrition Counselling', 'Orthopaedic Surgeon Consultation', 'Poision Ivy', 'Pregnancy Consultation', 'Rash', 'Referral for Pyshio/Chiro/Massage', 'Referral to a Psychologist', 'Referral to a Specialist', 'Requisition (Blood Test, X-Ray, Ultrasound, MRI, etc.)', 'Review Lab Results', 'Ringworm', 'STI', 'Shingles', 'Sick Note', 'Sinus Infection', 'Skin Health Consult', 'Skin Issues', 'Sleep Hygiene Counseling', 'Sleep Issues', 'Sore Throat', 'Sports Medicine', 'Sprains and Strains', 'Stress Reduction Counselling', 'Toenail or Fingernail Infection', 'Travel Consult', 'Treatment Prescriptions', 'Urinary Tract Infection', 'Varicose Veins', 'Weight Loss Monitoring/Counselling', 'Women\'s Health Assessment', 'Yeast Infections'];
var languages = ['Afar', 'Abkhazian', 'Afrikaans', 'Akan', 'Amharic', 'Aragonese', 'Arabic', 'Assamese', 'Avar', 'Aymara', 'Azerbaijani', 'Bashkir', 'Belarusian', 'Bulgarian', 'Bihari', 'Bislama', 'Bambara', 'Bengali', 'Tibetan', 'Breton', 'Bosnian', 'Catalan', 'Chechen', 'Chamorro', 'Corsican', 'Cree', 'Czech', 'Old Church Slavonic / Old Bulgarian', 'Chuvash', 'Welsh', 'Danish', 'German', 'Divehi', 'Dzongkha', 'Ewe', 'Greek', 'English', 'Esperanto', 'Spanish', 'Estonian', 'Basque', 'Persian', 'Peul', 'Finnish', 'Fijian', 'Faroese', 'French', 'West Frisian', 'Irish', 'Scottish Gaelic', 'Galician', 'Guarani', 'Gujarati', 'Manx', 'Hausa', 'Hebrew', 'Hindi', 'Hiri Motu', 'Croatian', 'Haitian', 'Hungarian', 'Armenian', 'Herero', 'Interlingua', 'Indonesian', 'Interlingue', 'Igbo', 'Sichuan Yi', 'Inupiak', 'Ido', 'Icelandic', 'Italian', 'Inuktitut', 'Japanese', 'Javanese', 'Georgian', 'Kongo', 'Kikuyu', 'Kuanyama', 'Kazakh', 'Greenlandic', 'Cambodian', 'Kannada', 'Korean', 'Kanuri', 'Kashmiri', 'Kurdish', 'Komi', 'Cornish', 'Kirghiz', 'Latin', 'Luxembourgish', 'Ganda', 'Limburgian', 'Lingala', 'Laotian', 'Lithuanian', 'Latvian', 'Malagasy', 'Marshallese', 'Maori', 'Macedonian', 'Malayalam', 'Mongolian', 'Moldovan', 'Marathi', 'Malay', 'Maltese', 'Burmese', 'Nauruan', 'North Ndebele', 'Nepali', 'Ndonga', 'Dutch', 'Norwegian Nynorsk', 'Norwegian', 'South Ndebele', 'Navajo', 'Chichewa', 'Occitan', 'Ojibwa', 'Oromo', 'Oriya', 'Ossetian', 'Punjabi', 'Pali', 'Polish', 'Pashto', 'Portuguese', 'Quechua', 'Raeto Romance', 'Kirundi', 'Romanian', 'Russian', 'Rwandi', 'Sanskrit', 'Sardinian', 'Sindhi', 'Sango', 'Serbo-Croatian', 'Sinhalese', 'Slovak', 'Slovenian', 'Samoan', 'Shona', 'Somalia', 'Albanian', 'Serbian', 'Swati', 'Southern Sotho', 'Sundanese', 'Swedish', 'Swahili', 'Tamil', 'Telugu', 'Tajik', 'Thai', 'Tigrinya', 'Turkmen', 'Tagalog', 'Tswana', 'Tonga', 'Turkish', 'Tsonga', 'Tatar', 'Twi', 'Tahitian', 'Uyghur', 'Ukrainian', 'Urdu', 'Venda', 'Vietnamese', 'Volapük', 'Walloon', 'Wolof', 'Xhosa', 'Yiddish', 'Yoruba', 'Zhuang', 'Chinese', 'Zulu'];

$(document).on('click', '.autocomplete-item', function() {
    var hiddenInput;
    if (this.className.includes('language-item')) {
        hiddenInput = $('#id_languages');
    } else {
        hiddenInput = $('#id_consultations');
    }
    str = this.innerText.slice(3);
    current = hiddenInput.val();
    start = current.indexOf(str);
    end = start + str.length + 2;
    if (end > current.length) {
        start = start - 2;
    }
    hiddenInput.val(current.slice(0, start) + current.slice(end));
    this.remove();
    console.log(hiddenInput.val());
});
function autocomplete(inp, arr) {
    var currentFocus;
    inp.addEventListener("input", function(e) {
        var a, b, i, val = this.value;
        closeAllLists();
        if (!val) { return false;}
        currentFocus = -1;
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        this.parentNode.appendChild(a);
        for (i = 0; i < arr.length; i++) {
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
    inp.addEventListener("keydown", function(e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
            currentFocus++;
            addActive(x);
        } else if (e.keyCode == 38) {
            currentFocus--;
            addActive(x);
        } else if (e.keyCode == 13) {
            e.preventDefault();
            if (currentFocus > -1) {
                if (x) x[currentFocus].click();
            }
            if (this.id == 'consult-input') {
                addToHidden(this, document.getElementById('id_consultations'), 'current-consults');
            } else if (this.id == 'language-input') {
                addToHidden(this, document.getElementById('id_languages'), 'current-languages');
            }
        }
    });
    function addActive(x) {
        if (!x) return false;
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
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