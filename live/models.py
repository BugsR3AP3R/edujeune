from django.db import models


class LiveSession(models.Model):
    STATUSES = [('scheduled', 'Programmé'), ('live', 'En Direct'), ('ended', 'Terminé')]

    course        = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='live_sessions')
    teacher       = models.ForeignKey('users.User', on_delete=models.CASCADE)
    title         = models.CharField(max_length=200)
    description   = models.TextField(blank=True)
    scheduled_at  = models.DateTimeField()
    started_at    = models.DateTimeField(null=True, blank=True)
    ended_at      = models.DateTimeField(null=True, blank=True)
    status        = models.CharField(max_length=20, choices=STATUSES, default='scheduled')
    stream_key    = models.CharField(max_length=64, blank=True)
    recording_url = models.URLField(blank=True)
    is_recorded   = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['-scheduled_at']
    def __str__(self): return f"[{self.status}] {self.title}"


class LiveMessage(models.Model):
    session    = models.ForeignKey(LiveSession, on_delete=models.CASCADE, related_name='messages')
    sender     = models.ForeignKey('users.User', on_delete=models.CASCADE)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['created_at']
