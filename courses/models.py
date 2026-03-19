from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name  = models.CharField(max_length=100)
    icon  = models.CharField(max_length=60, default='bi-book')
    color = models.CharField(max_length=20, default='#FF6B2B')
    slug  = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self): return self.name
    class Meta: verbose_name_plural = 'Categories'


class Course(models.Model):
    LEVELS  = [('beginner', 'Débutant'), ('intermediate', 'Intermédiaire'), ('advanced', 'Avancé')]
    STATUSES = [('draft', 'Brouillon'), ('published', 'Publié'), ('archived', 'Archivé')]

    title         = models.CharField(max_length=200)
    slug          = models.SlugField(unique=True, blank=True, max_length=255)
    description   = models.TextField()
    thumbnail     = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    teacher       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='courses_taught')
    category      = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    level         = models.CharField(max_length=20, choices=LEVELS, default='beginner')
    status        = models.CharField(max_length=20, choices=STATUSES, default='draft')
    is_free       = models.BooleanField(default=True)
    price         = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    language      = models.CharField(max_length=50, default='Français')
    requirements  = models.TextField(blank=True, default='')
    what_you_learn = models.TextField(blank=True, default='')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or 'cours'
            slug, n = base, 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"; n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def enrollment_count(self): return self.enrollments.count()

    @property
    def avg_rating(self):
        qs = self.reviews.all()
        return round(sum(r.rating for r in qs) / qs.count(), 1) if qs.exists() else 0

    @property
    def total_lessons(self):
        return sum(m.lessons.count() for m in self.modules.all())

    @property
    def total_duration(self):
        return sum(
            l.duration_minutes
            for m in self.modules.all()
            for l in m.lessons.all()
        )

    def __str__(self): return self.title
    class Meta: ordering = ['-created_at']


class Module(models.Model):
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    order       = models.PositiveIntegerField(default=0)
    is_locked   = models.BooleanField(default=False)

    class Meta: ordering = ['order']
    def __str__(self): return f"{self.course.title} › {self.title}"


class Lesson(models.Model):
    TYPES = [('video', 'Vidéo'), ('audio', 'Audio'), ('text', 'Texte'), ('live', 'Live')]

    module          = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title           = models.CharField(max_length=200)
    lesson_type     = models.CharField(max_length=10, choices=TYPES, default='video')
    content         = models.TextField(blank=True, default='', help_text='Texte ou description')
    video_file      = models.FileField(upload_to='videos/', null=True, blank=True)
    audio_file      = models.FileField(upload_to='audios/', null=True, blank=True)
    video_url       = models.URLField(blank=True, default='', help_text='URL YouTube / Vimeo / Drive')
    duration_minutes = models.IntegerField(default=0)
    order           = models.PositiveIntegerField(default=0)
    is_preview      = models.BooleanField(default=False)
    is_locked       = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['order']
    def __str__(self): return f"{self.module.title} › {self.title}"


class Enrollment(models.Model):
    student     = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='enrollments')
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress    = models.FloatField(default=0)
    completed   = models.BooleanField(default=False)

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']

    def __str__(self): return f"{self.student.username} → {self.course.title}"


class LessonProgress(models.Model):
    student      = models.ForeignKey('users.User', on_delete=models.CASCADE)
    lesson       = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed    = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta: unique_together = ['student', 'lesson']


class Review(models.Model):
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student    = models.ForeignKey('users.User', on_delete=models.CASCADE)
    rating     = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['course', 'student']
        ordering = ['-created_at']
