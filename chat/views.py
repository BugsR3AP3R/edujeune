from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Course, Enrollment
from .models import Classroom, Message


@login_required
def classroom(request, course_slug):
    course     = get_object_or_404(Course, slug=course_slug)
    is_teacher = request.user == course.teacher
    if not is_teacher:
        get_object_or_404(Enrollment, student=request.user, course=course)
    room, _ = Classroom.objects.get_or_create(course=course)
    msgs    = room.messages.select_related('sender').order_by('-created_at')[:80]
    return render(request, 'chat/classroom.html', {
        'course':     course,
        'room':       room,
        'messages':   list(reversed(list(msgs))),
        'is_teacher': is_teacher,
    })
