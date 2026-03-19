from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def home(request):
    from courses.models import Course, Category
    featured = Course.objects.filter(status='published').select_related('teacher', 'category').order_by('-created_at')[:6]
    categories = Category.objects.all()
    from users.models import User
    stats = {
        'courses': Course.objects.filter(status='published').count(),
        'students': User.objects.filter(role='student').count(),
        'teachers': User.objects.filter(role='teacher').count(),
    }
    features = [
        {'icon': 'bi-play-circle-fill',   'title': 'Cours Vidéo & Audio',       'desc': 'Leçons en vidéo, audio et texte organisées en modules. Suis ton rythme, reviens quand tu veux.'},
        {'icon': 'bi-broadcast',          'title': 'Lives Interactifs',          'desc': 'Sessions en direct programmables avec chat en temps réel. Pose tes questions au professeur.'},
        {'icon': 'bi-people-fill',        'title': 'Classrooms',                 'desc': 'Discute avec tes camarades de cours via un chat dédié à chaque cours. Apprenez ensemble.'},
        {'icon': 'bi-patch-question-fill','title': 'Quiz & Évaluations',         'desc': 'Teste tes connaissances avec des quiz chronométrés, score instantané et corrections détaillées.'},
        {'icon': 'bi-lock-fill',          'title': 'Accès & Contrôle',           'desc': 'Les profs contrôlent l\'accès : modules verrouillés, tentatives limitées, aperçu libre.'},
        {'icon': 'bi-award-fill',         'title': 'Points & Progression',       'desc': 'Gagne des points en complétant des leçons et quiz. Suis ta progression cours par cours.'},
    ]
    return render(request, 'base/home.html', {
        'featured_courses': featured,
        'categories': categories,
        'stats': stats,
        'features': features,
    })


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    from courses.models import Course, Enrollment
    from live.models import LiveSession
    ctx = {'user': request.user}
    if request.user.role == 'teacher':
        ctx['my_courses'] = Course.objects.filter(teacher=request.user).order_by('-created_at')
        ctx['total_students'] = Enrollment.objects.filter(
            course__teacher=request.user).values('student').distinct().count()
        ctx['lives'] = LiveSession.objects.filter(teacher=request.user).order_by('-scheduled_at')[:5]
    else:
        ctx['enrollments'] = Enrollment.objects.filter(
            student=request.user).select_related('course', 'course__teacher').order_by('-enrolled_at')
        ctx['lives'] = LiveSession.objects.filter(
            status__in=['scheduled', 'live'],
            course__enrollments__student=request.user
        ).distinct().order_by('scheduled_at')[:5]
    return render(request, 'base/dashboard.html', ctx)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        error = "Identifiants incorrects. Vérifie ton nom d'utilisateur et mot de passe."
    return render(request, 'users/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('home')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    errors = []
    post = {}
    if request.method == 'POST':
        from users.models import User
        post = request.POST
        username = post.get('username', '').strip()
        email = post.get('email', '').strip()
        first_name = post.get('first_name', '').strip()
        last_name = post.get('last_name', '').strip()
        password1 = post.get('password1', '')
        password2 = post.get('password2', '')
        role = post.get('role', 'student')

        if not username:
            errors.append("Le nom d'utilisateur est requis.")
        elif User.objects.filter(username=username).exists():
            errors.append("Ce nom d'utilisateur est déjà pris.")
        if not email:
            errors.append("L'email est requis.")
        elif User.objects.filter(email=email).exists():
            errors.append("Cet email est déjà utilisé.")
        if len(password1) < 6:
            errors.append("Le mot de passe doit avoir au moins 6 caractères.")
        elif password1 != password2:
            errors.append("Les mots de passe ne correspondent pas.")

        if not errors:
            user = User.objects.create_user(
                username=username, email=email, password=password1,
                first_name=first_name, last_name=last_name, role=role
            )
            login(request, user)
            messages.success(request, f"Bienvenue {first_name or username} ! 🎉")
            return redirect('dashboard')

    return render(request, 'users/register.html', {
        'errors': errors, 'post': post,
        'default_role': request.GET.get('role', 'student')
    })


@login_required
def my_profile(request):
    from courses.models import Course, Enrollment
    u = request.user
    ctx = {'profile_user': u, 'is_own': True}
    if u.role == 'teacher':
        ctx['courses'] = Course.objects.filter(teacher=u).order_by('-created_at')
    else:
        ctx['enrollments'] = Enrollment.objects.filter(student=u).select_related('course').order_by('-enrolled_at')
    return render(request, 'users/profile.html', ctx)


def user_profile(request, username):
    from users.models import User
    from courses.models import Course
    u = get_object_or_404(User, username=username)
    ctx = {'profile_user': u, 'is_own': request.user == u}
    if u.role == 'teacher':
        ctx['courses'] = Course.objects.filter(teacher=u, status='published').order_by('-created_at')
    return render(request, 'users/profile.html', ctx)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        u = request.user
        u.first_name = request.POST.get('first_name', u.first_name).strip()
        u.last_name = request.POST.get('last_name', u.last_name).strip()
        u.email = request.POST.get('email', u.email).strip()
        u.bio = request.POST.get('bio', u.bio)
        u.country = request.POST.get('country', u.country)
        if 'avatar' in request.FILES:
            u.avatar = request.FILES['avatar']
        u.save()
        messages.success(request, "✅ Profil mis à jour !")
        return redirect('profile')
    return render(request, 'users/edit_profile.html')
