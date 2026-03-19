from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLES = [('student', 'Étudiant'), ('teacher', 'Professeur'), ('admin', 'Admin')]
    role    = models.CharField(max_length=20, choices=ROLES, default='student')
    bio     = models.TextField(blank=True, default='')
    avatar  = models.ImageField(upload_to='avatars/', null=True, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Haïti')
    points  = models.IntegerField(default=0)

    @property
    def is_teacher(self): return self.role == 'teacher'

    @property
    def is_student(self): return self.role == 'student'

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    @property
    def initials(self):
        f = self.first_name[:1].upper() if self.first_name else ''
        l = self.last_name[:1].upper() if self.last_name else ''
        return f + l or self.username[:2].upper()

    def __str__(self):
        return f"{self.display_name} ({self.role})"
