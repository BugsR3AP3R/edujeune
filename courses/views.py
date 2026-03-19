from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Course, Module, Lesson, Enrollment, LessonProgress, Review, Category


# ─── PUBLIC ──────────────────────────────────────────────────────────────────

def course_list(request):
    qs = Course.objects.filter(status='published').select_related('teacher', 'category')
    q     = request.GET.get('q', '').strip()
    cat   = request.GET.get('cat', '')
    level = request.GET.get('level', '')
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(teacher__first_name__icontains=q))
    if cat:
        qs = qs.filter(category__slug=cat)
    if level:
        qs = qs.filter(level=level)
    return render(request, 'courses/list.html', {
        'courses': qs, 'categories': Category.objects.all(),
        'q': q, 'sel_cat': cat, 'sel_level': level,
    })


def course_detail(request, slug):
    course     = get_object_or_404(Course, slug=slug)
    is_enrolled = False
    enrollment  = None
    user_review = None
    if request.user.is_authenticated:
        enrollment  = Enrollment.objects.filter(student=request.user, course=course).first()
        is_enrolled = enrollment is not None
        user_review = Review.objects.filter(course=course, student=request.user).first()
    modules = course.modules.prefetch_related('lessons').all()
    reviews = course.reviews.select_related('student').all()
    return render(request, 'courses/detail.html', {
        'course': course, 'is_enrolled': is_enrolled,
        'enrollment': enrollment, 'modules': modules,
        'reviews': reviews, 'user_review': user_review,
    })


# ─── STUDENT ─────────────────────────────────────────────────────────────────

@login_required
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug, status='published')
    if request.user == course.teacher:
        return redirect('course_learn', slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
    if created:
        request.user.points += 5
        request.user.save()
        messages.success(request, f"✅ Inscrit(e) à « {course.title} » !")
    return redirect('course_learn', slug=slug)


@login_required
def course_learn(request, slug):
    course    = get_object_or_404(Course, slug=slug)
    is_teacher = request.user == course.teacher
    if not is_teacher:
        get_object_or_404(Enrollment, student=request.user, course=course)

    lesson_id      = request.GET.get('lesson')
    current_lesson = None
    if lesson_id:
        try:
            current_lesson = Lesson.objects.get(id=lesson_id, module__course=course)
        except Lesson.DoesNotExist:
            pass
    if not current_lesson:
        first_mod = course.modules.first()
        if first_mod:
            current_lesson = first_mod.lessons.first()

    completed_ids = set()
    if not is_teacher:
        completed_ids = set(LessonProgress.objects.filter(
            student=request.user, completed=True,
            lesson__module__course=course
        ).values_list('lesson_id', flat=True))

    modules = course.modules.prefetch_related('lessons').all()
    return render(request, 'courses/learn.html', {
        'course': course, 'is_teacher': is_teacher,
        'current_lesson': current_lesson,
        'completed_ids': completed_ids,
        'modules': modules,
    })


@login_required
def complete_lesson(request, lesson_id):
    lesson     = get_object_or_404(Lesson, id=lesson_id)
    course     = lesson.module.course
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    prog, _    = LessonProgress.objects.get_or_create(student=request.user, lesson=lesson)
    if not prog.completed:
        prog.completed    = True
        prog.completed_at = timezone.now()
        prog.save()
        total = sum(m.lessons.count() for m in course.modules.all())
        done  = LessonProgress.objects.filter(
            student=request.user, completed=True, lesson__module__course=course
        ).count()
        enrollment.progress = round(done / total * 100, 1) if total else 0
        if enrollment.progress >= 100:
            enrollment.completed = True
            request.user.points += 50
            request.user.save()
        enrollment.save()
        messages.success(request, f"✅ « {lesson.title} » complétée !")
    return redirect(f"/courses/{course.slug}/learn/?lesson={lesson.id}")


@login_required
def add_review(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.error(request, "Inscris-toi d'abord pour laisser un avis.")
            return redirect('course_detail', slug=slug)
        Review.objects.update_or_create(
            course=course, student=request.user,
            defaults={
                'rating':  int(request.POST.get('rating', 5)),
                'comment': request.POST.get('comment', '').strip(),
            }
        )
        messages.success(request, "Avis enregistré !")
    return redirect('course_detail', slug=slug)


@login_required
def my_courses(request):
    if request.user.role == 'teacher':
        courses = Course.objects.filter(teacher=request.user).order_by('-created_at')
        return render(request, 'courses/my_courses.html', {'courses': courses, 'is_teacher': True})
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course').order_by('-enrolled_at')
    return render(request, 'courses/my_courses.html', {'enrollments': enrollments, 'is_teacher': False})


# ─── TEACHER – COURSE ────────────────────────────────────────────────────────

@login_required
def create_course(request):
    if request.user.role != 'teacher':
        messages.error(request, "Seuls les professeurs peuvent créer des cours.")
        return redirect('dashboard')
    errors = []
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if not title:
            errors.append("Le titre est obligatoire.")
        if not errors:
            c = Course(
                title         = title,
                description   = request.POST.get('description', '').strip(),
                teacher       = request.user,
                level         = request.POST.get('level', 'beginner'),
                language      = request.POST.get('language', 'Français'),
                requirements  = request.POST.get('requirements', '').strip(),
                what_you_learn = request.POST.get('what_you_learn', '').strip(),
                is_free       = request.POST.get('is_free') == 'on',
                price         = float(request.POST.get('price', 0) or 0),
                status        = request.POST.get('status', 'draft'),
            )
            cat_id = request.POST.get('category')
            if cat_id:
                try: c.category = Category.objects.get(id=cat_id)
                except Category.DoesNotExist: pass
            if 'thumbnail' in request.FILES:
                c.thumbnail = request.FILES['thumbnail']
            c.save()
            messages.success(request, f"✅ Cours « {c.title} » créé ! Ajoutez des modules ci-dessous.")
            return redirect('manage_course', slug=c.slug)
    return render(request, 'courses/create.html', {
        'categories': Category.objects.all(),
        'errors': errors, 'post': request.POST,
    })


@login_required
def manage_course(request, slug):
    course       = get_object_or_404(Course, slug=slug, teacher=request.user)
    modules      = course.modules.prefetch_related('lessons').all()
    from live.models import LiveSession
    from quiz.models import Quiz
    return render(request, 'courses/manage.html', {
        'course':  course,
        'modules': modules,
        'lives':   course.live_sessions.order_by('-scheduled_at')[:5],
        'quizzes': Quiz.objects.filter(course=course),
    })


@login_required
def toggle_publish(request, slug):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    course.status = 'draft' if course.status == 'published' else 'published'
    course.save()
    messages.success(request, f"Cours {'publié' if course.status=='published' else 'mis en brouillon'} !")
    return redirect('manage_course', slug=slug)


# ─── TEACHER – MODULE ────────────────────────────────────────────────────────

@login_required
def add_module(request, slug):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if not title:
            messages.error(request, "Titre du module requis.")
        else:
            Module.objects.create(
                course      = course,
                title       = title,
                description = request.POST.get('description', '').strip(),
                order       = course.modules.count(),
                is_locked   = request.POST.get('is_locked') == 'on',
            )
            messages.success(request, f"✅ Module « {title} » ajouté !")
    return redirect('manage_course', slug=slug)


@login_required
def delete_module(request, module_id):
    mod = get_object_or_404(Module, id=module_id, course__teacher=request.user)
    slug = mod.course.slug
    mod.delete()
    messages.success(request, "Module supprimé.")
    return redirect('manage_course', slug=slug)


# ─── TEACHER – LESSON ────────────────────────────────────────────────────────

@login_required
def add_lesson(request, module_id):
    mod = get_object_or_404(Module, id=module_id, course__teacher=request.user)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if not title:
            messages.error(request, "Titre de la leçon requis.")
        else:
            lesson = Lesson(
                module           = mod,
                title            = title,
                lesson_type      = request.POST.get('lesson_type', 'video'),
                content          = request.POST.get('content', '').strip(),
                video_url        = request.POST.get('video_url', '').strip(),
                duration_minutes = int(request.POST.get('duration_minutes', 0) or 0),
                order            = mod.lessons.count(),
                is_preview       = request.POST.get('is_preview') == 'on',
                is_locked        = request.POST.get('is_locked') == 'on',
            )
            if 'video_file' in request.FILES: lesson.video_file = request.FILES['video_file']
            if 'audio_file' in request.FILES: lesson.audio_file = request.FILES['audio_file']
            lesson.save()
            messages.success(request, f"✅ Leçon « {title} » ajoutée !")
    return redirect('manage_course', slug=mod.course.slug)


@login_required
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course__teacher=request.user)
    if request.method == 'POST':
        lesson.title            = request.POST.get('title', lesson.title).strip()
        lesson.lesson_type      = request.POST.get('lesson_type', lesson.lesson_type)
        lesson.content          = request.POST.get('content', lesson.content).strip()
        lesson.video_url        = request.POST.get('video_url', lesson.video_url).strip()
        lesson.duration_minutes = int(request.POST.get('duration_minutes', lesson.duration_minutes) or 0)
        lesson.is_preview       = request.POST.get('is_preview') == 'on'
        lesson.is_locked        = request.POST.get('is_locked') == 'on'
        if 'video_file' in request.FILES: lesson.video_file = request.FILES['video_file']
        if 'audio_file' in request.FILES: lesson.audio_file = request.FILES['audio_file']
        lesson.save()
        messages.success(request, "✅ Leçon mise à jour !")
    return redirect('manage_course', slug=lesson.module.course.slug)


@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course__teacher=request.user)
    slug   = lesson.module.course.slug
    lesson.delete()
    messages.success(request, "Leçon supprimée.")
    return redirect('manage_course', slug=slug)
