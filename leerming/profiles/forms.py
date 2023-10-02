from django import forms
from django.utils.translation import gettext_lazy as _

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
        label=_("Jours de révision"),
    )
    review_time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}),
        initial="07:00",
        input_formats=["%H:%M"],
        label=_("Heure de révision"),
    )


class ProfileEditForm(ProfileForm):
    short_name = forms.CharField(max_length=50, label=_("Nom court"), required=False)
    full_name = forms.CharField(max_length=200, label=_("Nom complet"), required=False)
