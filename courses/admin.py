from django.contrib import admin
from .models import Category, Course, Module, Lesson, Enrollment, Review

admin.site.register(Category)
admin.site.register(Enrollment)
admin.site.register(Review)


class LessonInline(admin.TabularInline):
    model  = Lesson
    extra  = 1
    fields = ['title', 'lesson_type', 'video_url', 'duration_minutes', 'order', 'is_preview', 'is_locked']


class ModuleInline(admin.TabularInline):
    model  = Module
    extra  = 1
    fields = ['title', 'order', 'is_locked']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display       = ['title', 'teacher', 'category', 'level', 'status', 'enrollment_count', 'created_at']
    list_filter        = ['status', 'level', 'category']
    prepopulated_fields = {'slug': ('title',)}
    inlines            = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'is_locked']
    inlines      = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'lesson_type', 'duration_minutes', 'is_preview', 'is_locked']
    list_filter  = ['lesson_type', 'is_locked', 'is_preview']
