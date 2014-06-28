from django import forms


class PreferenceForm(forms.Form):

    registry = None

    def __init__(self, *args, **kwargs):

        self.preferences = kwargs.pop('preferences')
        super(PreferenceForm, self).__init__(*args, **kwargs)

        for preference in self.preferences:
            id = preference.section + "." + preference.name
            instance = preference.to_model()
            self.initial[id] = instance.value
            self.fields[id] = preference.field
