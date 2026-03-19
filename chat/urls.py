from django.urls import path
from . import views

urlpatterns = [
    path('classroom/<slug:course_slug>/', views.classroom, name='classroom'),
]
