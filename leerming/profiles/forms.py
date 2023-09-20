from django import forms

from .models import Profile


class ProfileForm(forms.Form):
    review_days = forms.MultipleChoiceField(choices=Profile.Weekday.choices)
    review_time = forms.TimeField()
