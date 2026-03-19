from django.db import models


class Quiz(models.Model):
    course             = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='quizzes')
    title              = models.CharField(max_length=200)
    description        = models.TextField(blank=True)
    time_limit_minutes = models.IntegerField(default=30)
    passing_score      = models.IntegerField(default=70)
    max_attempts       = models.IntegerField(default=3)
    is_locked          = models.BooleanField(default=False)
    created_at         = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.title

    def attempt_count_for(self, user):
        return self.attempts.filter(student=user).count()


class Question(models.Model):
    TYPES = [('single', 'Choix unique'), ('multiple', 'Choix multiple'), ('text', 'Texte libre')]
    quiz          = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text          = models.TextField()
    question_type = models.CharField(max_length=10, choices=TYPES, default='single')
    points        = models.IntegerField(default=1)
    order         = models.IntegerField(default=0)
    explanation   = models.TextField(blank=True)

    class Meta: ordering = ['order']
    def __str__(self): return self.text[:80]


class Choice(models.Model):
    question   = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text       = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order      = models.IntegerField(default=0)

    class Meta: ordering = ['order']
    def __str__(self): return self.text[:60]


class QuizAttempt(models.Model):
    student        = models.ForeignKey('users.User', on_delete=models.CASCADE)
    quiz           = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score          = models.FloatField(default=0)
    passed         = models.BooleanField(default=False)
    started_at     = models.DateTimeField(auto_now_add=True)
    finished_at    = models.DateTimeField(null=True, blank=True)
    attempt_number = models.IntegerField(default=1)

    class Meta: ordering = ['-started_at']


class Answer(models.Model):
    attempt          = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question         = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(Choice, blank=True)
    text_answer      = models.TextField(blank=True)
    is_correct       = models.BooleanField(default=False)
