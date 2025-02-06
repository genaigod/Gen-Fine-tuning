from django.urls import path
from . import views

app_name = 'api_auth'
urlpatterns = [
    path('__user/',views.UserView.as_view(),name='user'),
]