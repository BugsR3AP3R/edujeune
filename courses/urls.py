from django.urls import path
from . import views

urlpatterns = [
    path('',                                      views.course_list,    name='course_list'),
    path('my/',                                   views.my_courses,     name='my_courses'),
    path('create/',                               views.create_course,  name='create_course'),

    path('<slug:slug>/',                          views.course_detail,  name='course_detail'),
    path('<slug:slug>/enroll/',                   views.enroll,         name='enroll'),
    path('<slug:slug>/learn/',                    views.course_learn,   name='course_learn'),
    path('<slug:slug>/review/',                   views.add_review,     name='add_review'),
    path('<slug:slug>/manage/',                   views.manage_course,  name='manage_course'),
    path('<slug:slug>/manage/publish/',           views.toggle_publish, name='toggle_publish'),
    path('<slug:slug>/manage/module/add/',        views.add_module,     name='add_module'),

    path('module/<int:module_id>/delete/',        views.delete_module,  name='delete_module'),
    path('module/<int:module_id>/lesson/add/',    views.add_lesson,     name='add_lesson'),

    path('lesson/<int:lesson_id>/complete/',      views.complete_lesson, name='complete_lesson'),
    path('lesson/<int:lesson_id>/edit/',          views.edit_lesson,    name='edit_lesson'),
    path('lesson/<int:lesson_id>/delete/',        views.delete_lesson,  name='delete_lesson'),
]
