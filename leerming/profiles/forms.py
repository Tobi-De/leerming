from django import forms

from .models import Profile


class ProfileForm(forms.Form):
    review_days = forms.MultipleChoiceField(
        choices=Profile.Weekday.choices,
        initial=[
            Profile.Weekday.MONDAY,
            Profile.Weekday.TUESDAY,
            Profile.Weekday.WEDNESDAY,
            Profile.Weekday.THURSDAY,
            Profile.Weekday.FRIDAY,
            Profile.Weekday.SATURDAY,
            Profile.Weekday.SUNDAY,
        ],
    )
    review_time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}), initial="07:00"
    )
