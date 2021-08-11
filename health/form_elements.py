from django import forms

class customTextInputWidget(forms.TextInput):
    def __init__(self, _type, placeholder, _id, extra_classes='', exargs={}):
        self.attrs = {
            'type': _type,
            'class': 'formcontrol' + (f' {extra_classes}' if extra_classes else ''),
            'placeholder': placeholder,
        }
        if _id:
            self.attrs['id'] = _id
        if exargs:
            self.attrs.update(exargs)

def customDateInputWidget(placeholder, extra_classes='', _id=''):
    newWidget = forms.DateInput(attrs = {
        'type': 'text',
        "onfocus": "(this.type='date')",
        "onblur": "(this.value ? this.type='date' : this.type='text')",
        'class': 'form-control' + (f' {extra_classes}' if extra_classes else ''),
        'placeholder': placeholder,
    })
    if _id:
        newWidget.attrs['id'] = _id
    return newWidget