import secrets
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Course, Enrollment
from .models import LiveSession, LiveMessage


@login_required
def upcoming_lives(request):
    if request.user.role == 'teacher':
        sessions = LiveSession.objects.filter(teacher=request.user).order_by('-scheduled_at')
    else:
        sessions = LiveSession.objects.filter(
            status__in=['scheduled', 'live'],
            course__enrollments__student=request.user
        ).distinct().order_by('scheduled_at')
    return render(request, 'live/upcoming.html', {'sessions': sessions})


@login_required
def schedule_live(request, slug):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if not title:
            messages.error(request, "Le titre est requis.")
        else:
            LiveSession.objects.create(
                course       = course,
                teacher      = request.user,
                title        = title,
                description  = request.POST.get('description', '').strip(),
                scheduled_at = request.POST.get('scheduled_at'),
                is_recorded  = request.POST.get('is_recorded') == 'on',
                stream_key   = secrets.token_hex(16),
            )
            messages.success(request, "✅ Live programmé !")
            return redirect('manage_course', slug=slug)
    return render(request, 'live/schedule.html', {'course': course})


@login_required
def live_room(request, session_id):
    session    = get_object_or_404(LiveSession, id=session_id)
    is_teacher = request.user == session.teacher
    if not is_teacher:
        if not Enrollment.objects.filter(student=request.user, course=session.course).exists():
            messages.error(request, "Inscris-toi au cours pour accéder au live.")
            return redirect('course_detail', slug=session.course.slug)
    msgs = session.messages.select_related('sender').order_by('-created_at')[:80]
    return render(request, 'live/room.html', {
        'session':    session,
        'is_teacher': is_teacher,
        'messages':   list(reversed(list(msgs))),
    })
