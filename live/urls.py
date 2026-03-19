from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.upcoming_lives, name='upcoming_lives'),
    path('schedule/<slug:slug>/',         views.schedule_live,  name='schedule_live'),
    path('room/<int:session_id>/',        views.live_room,      name='live_room'),
]
