from django.urls import path
from . import views

app_name = 'workorders'

urlpatterns = [
    path('notification/<int:notification_id>/accept/', views.accept_notification, name='accept_notification'),
    path('notification/<int:notification_id>/start/', views.start_notification, name='start_notification'),
    path('notification/<int:notification_id>/complete/', views.complete_notification, name='complete_notification'),
]
