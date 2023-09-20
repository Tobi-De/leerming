from django.http import HttpRequest
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from .forms import ProfileForm


def create(request:HttpRequest):
    form = ProfileForm(request.POST or None)
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            # TODO
            return redirect('cards:index')
    else:
        form = ProfileForm()
    return TemplateResponse(request, 'profiles/create.html', {'form': form})
