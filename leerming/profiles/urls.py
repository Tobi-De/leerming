from django.urls import path

app_name = 'profiles'

urlpatterns = [path("create/". views.create, name="create")]
