from django.db import models


class Classroom(models.Model):
    course     = models.OneToOneField('courses.Course', on_delete=models.CASCADE, related_name='classroom')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"Classroom — {self.course.title}"


class Message(models.Model):
    classroom  = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='messages')
    sender     = models.ForeignKey('users.User', on_delete=models.CASCADE)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['created_at']
    def __str__(self): return f"{self.sender.username}: {self.content[:40]}"
