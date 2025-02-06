from django.urls import path
from . import views

app_name = 'kohya_ss'
urlpatterns = [
    path('TrainTask/', views.TrainTask.as_view(),name='TrainTask'),
    path('IsTraining/', views.IsTraining.as_view(),name='IsTraining'),
    path('CancelTrain/', views.CancelTrain.as_view(),name='CancelTrain'),
    path('Qsize/', views.Qsize.as_view(),name='Qsize'),
]