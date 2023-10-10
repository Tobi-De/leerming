from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Profile


class ProfileForm(forms.ModelForm):
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
        widget=forms.SelectMultiple(attrs={"class": "tom-select"}),
    )

    class Meta:
        model = Profile
        fields = ["review_days", "review_time", "timezone"]
        widgets = {
            "timezone": forms.Select(attrs={"class": "tom-select"}),
            "review_time": forms.TimeInput(format="%H:%M"),
        }

    def clean(self):
        cleaned_data = self.cleaned_data
        review_days = cleaned_data.get("review_days")
        review_days = [int(day) for day in review_days]
        cleaned_data["review_days"] = review_days
        return cleaned_data


class ProfileEditForm(ProfileForm):
    class Meta(ProfileForm.Meta):
        fields = ProfileForm.Meta.fields + [
            "short_name",
            "full_name",
            "email_notifications_enabled",
        ]
